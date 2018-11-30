"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from datetime import datetime
from flaskblog import login_manager
from flask_login import UserMixin
from flask import flash
import pymysql
import os

@login_manager.user_loader
def load_user(user_id):
    db = db_model()
    data = db.get_user_by_id(user_id)
    user = User(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][6], data[0][7], data[0][8])
    return user

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
	    cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, role, school_id FROM users WHERE user_id = %s", (id))
	    return cur.fetchall()

	def get_user_by_username(self, username):
		cur = self.conn.cursor()
		cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, role, school_id FROM users WHERE username = %s", (username))
		return cur.fetchall()

	def get_user_by_email(self, email):
	    cur = self.conn.cursor()
	    cur.execute("SELECT user_id, username, first_name, last_name, email, picture, ssb, role, school_id FROM users WHERE email = %s", (email))
	    return cur.fetchall()

	def add_user(self, username, first_name, last_name, email, picture, password, school_id):
		cur = self.conn.cursor()
		cur.execute("INSERT INTO users(username, first_name, last_name, email, picture, ssb, role, school_id) VALUES(%s, %s, %s, %s, %s, %s, 'user', %s)", 
					(username, first_name, last_name, email, picture, password, school_id))
		self.conn.commit()

	def get_all_school_names(self):
		cur = self.conn.cursor()
		cur.execute("SELECT school_id, school_name FROM schools")
		return cur.fetchall()