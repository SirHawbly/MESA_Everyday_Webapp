"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import render_template, url_for, flash, redirect, request
<<<<<<< HEAD:flaskblog/routes.py
from flaskblog import app, bcrypt,mail
from flaskblog.forms import RegistrationForm, LoginForm,RequestResetForm, ResetPasswordForm
from flaskblog.models import User, db_model
=======
from MESAeveryday import app, bcrypt
from MESAeveryday.forms import RegistrationForm, LoginForm
from MESAeveryday.models import User, Role, UserRole, School, Badge, Stamp, UserStamp, loadSession
>>>>>>> dafc2c61685a869a239b162d46fb546ad4a36cbb:MESAeveryday/routes.py
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/", methods=['GET', 'POST'])
# Millen's Added code for a merged landing page
@app.route("/landpage", methods=['GET', 'POST'])
def landpage():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form_register = RegistrationForm()
    form_login = LoginForm()
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)
	
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Registration Form Submitted
    form_register = RegistrationForm()
    form_login = LoginForm()
    if form_register.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')
        new_user = User(form_register.username.data, form_register.firstname.data, form_register.lastname.data,
                    form_register.email.data, hashed_password, form_register.school.data)        
        session = loadSession()			
        session.add(new_user)
        session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('landpage'))
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)
		
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Login Form Submitted
    form_register = RegistrationForm()
    form_login = LoginForm()
    if form_login.validate_on_submit():
        session = loadSession()
        user = session.query(User).filter(User.username==form_login.username.data).first()		
        if user and bcrypt.check_password_hash(user.password, form_login.password.data):
            login_user(user, remember=form_login.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)

@app.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard():
    session = loadSession()     
    result=[row.badge_name for row in session.query(Badge.badge_name)]
    return render_template('dashboard.html', result = result)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('landpage'))

"""
    Minh N:
"""

def send_reset_email(useremail,user):

    token = user.get_reset_token()

    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[useremail])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

"""
    Minh N:
"""
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        db = db_model()
        user = db.get_user_by_email(form.email.data)
        myuser = User(user[0][0], user[0][1], user[0][2], user[0][4])

        #user = db.count('minhnpdx1@gmail.com')

       # user=db.get_user_by_username('minh9')
        send_reset_email(user[0][2],myuser)
        flash(user[0][2],'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

"""
    MinhN:
"""

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        User.password = hashed_password
        db=db_model()
        db.update_password_by_username(User.password,user[0][1])

        #user=User.password
      #  db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)