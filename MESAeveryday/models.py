"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from MESAeveryday import login_manager, app, bcrypt
from flask_login import UserMixin
from flask import flash
#import pymysql
import os
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

# from contextlib import contextmanager

#db_connection uses mysql+pymysql as otherwise certain libraries that are not supported by python3 will need to be installed
#check link to it here: https://stackoverflow.com/questions/22252397/importerror-no-module-named-mysqldb
db_connection = 'mysql+pymysql://' + os.environ['MESAusername'] + ':' + os.environ['MESApassword'] + '@' + os.environ['MESAhostname'] + ':3306/' + os.environ['MESAusername']

engine = create_engine(db_connection)
Base = declarative_base(engine)

metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()

# do not delete those until the new loadSession method is proved working
# def loadSession():
#     metadata = Base.metadata
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session

# @contextmanager
# def loadSession():
#     metadata = Base.metadata
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#     finally:
#         session.close()

# need a session that will not be closed to use current_user
# def loadLoginSession():
#     metadata = Base.metadata
#     Session = sessionmaker(bind=engine, expire_on_commit=False)
#     session = Session()
#     return session

@login_manager.user_loader
def load_user(user_id):
    # with loadSession() as session:
    try:
        return session.query(User).filter(User.id==user_id).first()
    except:
        session.rollback()
        return None        
        
#All classes here are based on a table in the database. If a change is made to the database, those changes must be reflected here as well


#Class for the "user_roles" table
class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    def __init__(self, user_id, role_id):
	    self.user_id = user_id
	    self.role_id = role_id

#Class for the "roles" table
class Role(Base):
    __tablename__ = 'roles'

    id = Column('role_id', Integer, primary_key=True)
    name = Column('role_name', String)
    description = Column(String)

    def __init__(self, name, description):
	    self.name = name
	    self.description = description

#Class for the "users" table
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column('user_id', Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    email = Column(String)
    picture = Column(String) #This needs to be deleted after the picture column in the database is deleted
    school_id = Column(Integer, ForeignKey("schools.school_id"))
    avatar_id = Column(Integer, ForeignKey("avatars.id"))
    password = Column('SSB', String)
    last_login = Column(DateTime)

    school = relationship("School", foreign_keys=[school_id])
    avatar = relationship("Avatar", foreign_keys=[avatar_id])
    role = relationship('Role', secondary='user_roles',
                         backref=backref('users', lazy='dynamic'))


    def __init__(self, username, first_name, last_name, email, password, school_id):
        self.username = username
        self.email = email
        self.picture = 'default.png' #This needs to be deleted after the picture column in the database is deleted
        self.avatar_id = 1
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.school_id = school_id

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        # with loadSession() as session:
        return session.query(User).filter(User.id==user_id).first()
        
    def get_all_username():
        try:
            return session.query(User.username)
        except:
            session.rollback()
            return None

    def validate_username(username):
        try:
            user = session.query(User).filter(User.username == username.data).first()
        except:
            session.rollback()
            user = None
        if user:
            return True
        else:
            return False

    def validate_email(email):
        try:
            user = session.query(User).filter(User.email == email.data).first()
        except:
            session.rollback()
            user = None
        if user:
            # test whether false will be returned
            return True
        else:
            return False

    def add_new_user(new_user):
        # with loadSession() as session:
        try:
            session.add(new_user)
        except:
            session.rollback()

    def get_user_by_email(email):
        # with loadSession() as session:
        try:
            return session.query(User).filter(User.email == email).first()
        except:
            session.rollback()
            return None

    def get_user_by_username(username):
        try:
            return session.query(User).filter(User.username == username).first()
        except:
            session.rollback()
            return None

    def reset_pwd(id, hashed_pwd):
        # with loadSession() as session:
        #once a session is loaded we want to get the row
        #where User.id matches the id of the user returned by User.verify_reset_token(token)
        #this insures that the password for the correct user will be the one changed
        try:
            row = session.query(User).filter(User.id == id).first()
        #Change the password is a simple assign statement
            row.password = hashed_pwd
        except:
            session.rollback()
            return False
        return True
        
    def update_last_login(id, new_last_login):     
        try:
            row = session.query(User).filter(User.id == id).first()
            row.last_login = new_last_login
        except:
            session.rollback()
            return False
        return True
        
    def update_name(id, new_first_name, new_last_name):     
        try:
            row = session.query(User).filter(User.id == id).first()
            row.first_name = new_first_name
            row.last_name = new_last_name
        except:
            session.rollback()
            return False
        return True
        
    def update_email(id, new_email):     
        try:
            row = session.query(User).filter(User.id == id).first()
            row.email = new_email
        except:
            session.rollback()
            return False
        return True  

    def update_school(id, new_school_id):     
        try:
            row = session.query(User).filter(User.id == id).first()
            row.school_id = new_school_id
        except:
            session.rollback()
            return False
        return True 
        
    def update_avatar(id, new_avatar_id):     
        try:
            row = session.query(User).filter(User.id == id).first()
            row.avatar_id = new_avatar_id
        except:
            session.rollback()
            return False
        return True 
    
    def get_badge_progress(user_id, badge_id):
        try:
            return session.execute("SELECT total_points, current_level, to_next_level FROM user_aggregate WHERE user_id = :user_id AND badge_id = :badge_id", {'user_id':user_id, 'badge_id':badge_id}).first()
        except:
            session.rollback()
            return None
        
#Class for the "schools" table
class School(Base):
    __tablename__ = 'schools'

    school_id = Column(Integer, primary_key=True)
    school_name = Column(String)
    district = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)

    def __init__(self, school_name, district, city, state, zip_code):
	    self.school_name = school_name
	    self.district = district
	    self.city = city
	    self.state = state
	    self.zip_code = zip_code

    def get_all_schools_names():
        # with loadSession() as session:
        try:
            # The union ensures that the "Other" will always be found at the end
            results = session.query(School.school_id, School.school_name).filter(School.school_name != 'Other').order_by(School.school_name.asc())\
                .union(session.query(School.school_id, School.school_name).filter(School.school_name == 'Other'))
            return results
        except:
            session.rollback()
            return None

#Class for the "badges" table
class Badge(Base):
    __tablename__ = 'badges'

    badge_id = Column(Integer, primary_key=True)
    badge_name = Column(String)
    color = Column(String)
    picture = Column(String)
    level1_points = Column(Integer)
    level2_points = Column(Integer)
    level3_points = Column(Integer)
    level4_points = Column(Integer)
    level5_points = Column(Integer)
    level6_points = Column(Integer)
    level7_points = Column(Integer)
    level8_points = Column(Integer)
    level9_points = Column(Integer)
    level10_points = Column(Integer)

    def __init__(self, badge_name, color, level1_points, level2_points, level3_points, level4_points,
                    level5_points, level6_points, level7_points, level8_points, level9_points, level10_points):
        self.badge_name = badge_name
        self.level1_points = level1_points
        self.level2_points = level2_points
        self.level3_points = level3_points
        self.level4_points = level4_points
        self.level5_points = level5_points
        self.level6_points = level6_points
        self.level7_points = level7_points
        self.level8_points = level8_points
        self.level9_points = level9_points
        self.level10_points = level10_points

    def get_all_badges_names():
        try:
            return session.query(Badge.badge_name)
        except:
            session.rollback()
            return None

    def get_all_badges_id_with_names():
        try:
            return session.query(Badge.badge_id, Badge.badge_name)
        except:
            session.rollback()
            return None

    def get_badge_name(badge_id):
        try:
            return session.query(Badge.badge_name).filter(Badge.badge_id == badge_id)
        except:
            session.rollback()
            return None

    def get_badge_picture(badge_id):
        try:
            return session.query(Badge.picture).filter(Badge.badge_id == badge_id)
        except:
            session.rollback()
            return None


#Class for the "stamps" table
class Stamp(Base, UserMixin):
    __tablename__ = 'stamps'

    stamp_id = Column(Integer, primary_key=True)
    stamp_name = Column(String)
    badge_id = Column(Integer, ForeignKey("badges.badge_id"))
    points = Column(Integer)
    url = Column(String)

    badge = relationship("Badge", foreign_keys=[badge_id])

    def __init__(self, stamp_name, badge_id, points, url):
        self.stamp_name = stamp_name
        self.badge_id = badge_id
        self.points = points
        self.url = url

    def get_stamps_of_badge(badge_id):
        try:
            return session.query(Stamp.stamp_id, Stamp.stamp_name).filter(Stamp.badge_id == badge_id)
        except:
            session.rollback()
            return None

    def get_unearned_stamps_of_badge(user_id, badge_id):
        try:
            subquery = session.query(UserStamp.stamp_id).filter(UserStamp.user_id == user_id)
            return session.query(Stamp).filter(Stamp.badge_id == badge_id).filter(Stamp.stamp_id.notin_(subquery))
        except:
            session.rollback()
            return None

    def get_earned_stamps_of_badge(user_id, badge_id):
        try:
            subquery = session.query(UserStamp.stamp_id).filter(UserStamp.user_id == user_id)
            return session.query(Stamp).filter(Stamp.badge_id == badge_id).filter(Stamp.stamp_id.in_(subquery))
        except:
            session.rollback()
            return None        
    
    def get_earned_points(user_id, badge_id):
        try:
            # subquery = session.query(UserStamp.stamp_id).filter(UserStamp.user_id == user_id)
            # return session.query(Stamp).filter(Stamp.badge_id == badge_id).filter(Stamp.stamp_id.in_(subquery))
            return session.query(UserStamp.stamp_id, Stamp.points).filter(UserStamp.user_id == user_id).filter(UserStamp.stamp_id == Stamp.stamp_id).filter(Stamp.badge_id == badge_id)
        except:
            session.rollback()
            return None

#Class for the "user_stamps" table
class UserStamp(Base, UserMixin):
    __tablename__ = 'user_stamps'

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    stamp_id = Column(Integer, ForeignKey("stamps.stamp_id"), primary_key=True)
    log_date = Column(DateTime, primary_key=True)
    stamp_date = Column(Date)

    user = relationship("User", foreign_keys=[user_id])
    stamp = relationship("Stamp", foreign_keys=[stamp_id])

    def __init__(self, user_id, stamp_id, log_date, stamp_date):
        self.user_id = user_id
        self.stamp_id = stamp_id
        self.log_date = log_date
        self.stamp_date = stamp_date
        
    def get_earned_stamp(user_id):
        try:
            return session.query(UserStamp.stamp_id).filter(UserStamp.user_id == user_id)
        except:
            session.rollback()
            return None

    def earn_stamp(user_id, stamp_id, log_date, stamp_date):
        # with loadSession() as session:
        new_UserStamp = UserStamp(user_id, stamp_id, log_date, stamp_date)
        try:
            session.add(new_UserStamp)
            session.commit()
        except:
            session.rollback()
            return False
        return True

#Class for the "avatars" table
class Avatar(Base):
    __tablename__ = 'avatars'

    id = Column(Integer, primary_key=True)
    file_name = Column(String)

    def __init__(self, file_name):
	    self.file_name = feile_name
        
    def get_all_avatars():
        try:
            return session.query(Avatar)
        except:
            session.rollback()
            return None        



'''
class User(UserMixin):
	def __init__(self, id, username, first_name, last_name, email, password, role, school_id):
	    self.id = id
	    self.username = username
	    self.email = email
	    self.image_file = 'default.jpg'
	    self.password = password
	    self.first_name = first_name
	    self.last_name = last_name
	    self.role = role
	    self.school_id = school_id

class db_model():
	def __init__(self):
	    self.conn = pymysql.connect(host=os.environ['MESAhostname'], port=3306, user=os.environ['MESAusername'], passwd=os.environ['MESApassword'], db=os.environ['MESAusername'])

	def get_user_by_id(self, id):
	    cur = self.conn.cursor()
	    cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, school_id FROM users WHERE user_id = %s", (id))
	    return cur.fetchall()

	def get_user_by_username(self, username):
		cur = self.conn.cursor()
		cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, school_id FROM users WHERE username = %s", (username))
		return cur.fetchall()

	def get_user_by_email(self, email):
	    cur = self.conn.cursor()
	    cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, school_id FROM users WHERE email = %s", (email))
	    return cur.fetchall()

	def add_user(self, username, first_name, last_name, email, picture, password, school_id):
		cur = self.conn.cursor()
		cur.execute("INSERT INTO users(username, first_name, last_name, email, picture, ssb, school_id) VALUES(%s, %s, %s, %s, %s, %s, 'user', %s)",
					(username, first_name, last_name, email, picture, password, school_id))
		self.conn.commit()

	def get_all_school_names(self):
		cur = self.conn.cursor()
		cur.execute("SELECT school_id, school_name FROM schools")
		return cur.fetchall()

	def view_badge(self):
		cur = self.conn.cursor()
		cur.execute("SELECT badge_name FROM badges")
		rows = cur.fetchall()
		rows=[i[0] for i in rows]
		return rows
'''
