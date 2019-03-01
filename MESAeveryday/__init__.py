"""
This file initializes the application then imports all the routes from routes.py 

Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['WTF_CSRF_ENABLED'] = False
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'devtestmesa@gmail.com'
app.config['MAIL_PASSWORD'] = 'd3v4354M35@'
limiter = Limiter(
    app,
    key_func = get_remote_address,
    default_limits = ['400 per day', '100 per hour']
)
mail = Mail(app)

from MESAeveryday import routes
