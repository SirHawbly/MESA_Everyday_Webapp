"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
# Added by Millen
# from flask_security import Security, SQLAlchemyUserDatastore

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
