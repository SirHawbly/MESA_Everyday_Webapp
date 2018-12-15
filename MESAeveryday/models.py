"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from datetime import datetime
from MESAeveryday import login_manager, bcrypt, app, admin
from flask_login import UserMixin
from flask import flash
#import pymysql
import os
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
# Added by Millen
from flask_security import current_user
from flask_admin.contrib import sqla
# from flask_security import Security, SQLAlchemyUserDatastore

db_connection = 'mysql://' + os.environ['MESAusername'] + ':' + os.environ['MESApassword'] + '@' + os.environ['MESAhostname'] + ':3306/' + os.environ['MESAusername']
engine = create_engine(db_connection)
Base = declarative_base(engine)

def loadSession():
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# Added by Millen
"""
View for the administrator
Modified from flask-admin example
https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
"""
class AdminView(sqla.ModelView):
    # Prevent normal users from accessing admin view
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('landpage'))

# Added by Millen
def admin_create():
    # Setup Flask-Security from Flask-Admin examples
    session = loadSession()
    """
    user_datastore = SQLAlchemyUserDatastore(session, User, Role)
    security = Security(app, user_datastore)
    """
    if(session.query(User).filter(User.username=="admin").first()):
        flash('Admin already created')
    else:
        # admin init
        admin.add_view(AdminView(Role,session))
        admin.add_view(AdminView(User,session))

        hard_admin = User(admin, admin, admin, mwan@pdx.edu, bcrypt.generate_password_hash("password").decode('utf-8'), 1)
        session.add(hard_admin)
        session.commit()

        flash('Creating Admin')

@login_manager.user_loader
def load_user(user_id):
    session = loadSession()
    return session.query(User).filter(User.id==user_id).first()

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
    picture = Column(String)
    school_id = Column(Integer, ForeignKey("schools.school_id"))
    password = Column('SSB', String)
    last_login = (DateTime)

    school = relationship("School", foreign_keys=[school_id])
    role = relationship('Role', secondary='user_roles',
                         backref=backref('users', lazy='dynamic'))


    def __init__(self, username, first_name, last_name, email, password, school_id):
        self.username = username
        self.email = email
        self.picture = 'default.jpg'
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.school_id = school_id

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

#Class for the "badges" table
class Badge(Base):
    __tablename__ = 'badges'

    badge_id = Column(Integer, primary_key=True)
    badge_name = Column(String)
    color = Column(String)
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
