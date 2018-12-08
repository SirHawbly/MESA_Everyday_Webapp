"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from datetime import datetime
from flaskblog import login_manager,app
from flask_login import UserMixin
from flask import flash
import pymysql
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    db = db_model()
    data = db.get_user_by_id(user_id)
    user = User(data[0][0], data[0][1], data[0][2], data[0][4])
    return user



class User(UserMixin):
	def __init__(self, id, username, email, password):
	    self.id = id
	    self.username = username
	    self.email = email
	    self.image_file = 'default.jpg'
	    self.password = password

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
		#return User.query.get(user_id)
		model = db_model()
		return model.get_user_by_id(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class db_model():
	def __init__(self):
	    self.conn = pymysql.connect(host='67.160.141.91', port=3306, user='flaskblog_user', passwd='test', db='flaskblog_db')

	def get_user_by_id(self, id):
	    cur = self.conn.cursor()
	    cur.execute("SELECT id, username, email, image_file, password, role FROM users WHERE id = %s", (id))
	    return cur.fetchall()

	def get_user_by_username(self, username):
		cur = self.conn.cursor()
		cur.execute("SELECT id, username, email, image_file, password, role FROM users WHERE username = %s", (username))
		return cur.fetchall()

	def get_user_by_email(self, email):
	    cur = self.conn.cursor()
	    cur.execute("SELECT id, username, email, image_file, password, role FROM users WHERE email = %s", (email))
	    return cur.fetchall()

	def get_next_id(self):
	    cur = self.conn.cursor()
	    cur.execute("SELECT MAX(ID) FROM users")
	    return cur.fetchall()[0][0]	+ 1

	def add_user(self, id, username, email, image_file, password):
		cur = self.conn.cursor()
		cur.execute("INSERT INTO users(id, username, email, image_file, password, role) VALUES(%s, %s, %s, %s, %s, 'user')", (id, username, email, image_file, password))
		self.conn.commit()

	"""
		MinhN: This is my test  function
	"""
	def count(self,email):
		cur = self.conn.cursor()
		cur.execute("SELECT count(*) FROM users WHERE email = %s", (email))
		return cur.fetchall()

	"""
		MinhN: This function update the password by username
	"""
	def update_password_by_username(self,password,username):
		cur = self.conn.cursor()
		cur.execute("Update users SET password=%s  WHERE username = %s",(password,username))

		self.conn.commit()