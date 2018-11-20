"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, db_model
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/", methods=['GET', 'POST'])
# Millen's Added code for a merged landing page
@app.route("/landpage", methods=['GET', 'POST'])
def landpage():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form_register = RegistrationForm()
    form_login = LoginForm()
    # Registration Form Submitted
    if form_register.is_submitted():
        if form_register.validate():
            hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')
            db = db_model()
            id = db.get_next_id()
            db.add_user(id, form_register.username.data, form_register.email.data, 'default.jpg', hashed_password)
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('landpage'))
    # Login Form Submitted
    elif form_login.is_submitted():
        if form_login.validate():
            db = db_model()
            data = db.get_user_by_email(form_login.email.data)
            if data and bcrypt.check_password_hash(data[0][4], form_login.password.data):
                user = User(data[0][0], data[0][1], data[0][2], data[0][4])
                login_user(user, remember=form_login.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    # Render both
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html', title='Dashboard')
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landpage'))

