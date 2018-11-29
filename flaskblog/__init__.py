"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flaskblog.views import MyModelView
from flaskblog.models import User, Role, db_model


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Millen's admin creation
# Modified from Flask-Admin example
# https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
admin = flask_admin.Admin(app,)
# add model views
admin.add_view(MyModelView(Role, db_model))
admin.add_view(MyModelView(User, db_model))
from flaskblog import routes
