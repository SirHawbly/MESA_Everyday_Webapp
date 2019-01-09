"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import render_template, url_for, flash, redirect, request,session
from MESAeveryday import app, bcrypt, mail
from MESAeveryday.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,RequestResetUserForm,UpdateAccountForm
from MESAeveryday.models import User, Role, UserRole, School, Badge, Stamp, UserStamp, loadSession
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import secrets
from PIL import Image
import os
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
        # Generate username
        new_username = generate_username(form_register.firstname.data, form_register.lastname.data, random_code())
        all_usernames = [row.username for row in User.get_all_username()]
        new_username = check_username(new_username, all_usernames)
        
        if new_username == 'ERROR':
            flash('Sorry, we were unable to generate an account for you.', 'danger')
        else:
        
            # Generate hashed password
            hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')
      
            # Add user to the database
            new_user = User(new_username, form_register.firstname.data, form_register.lastname.data,
                    form_register.email.data, hashed_password, form_register.school.data)
            session = loadSession()
            session.add(new_user)
            session.commit()
        
            # Tell the user their new username and send them an email with the username
            flash('Your account has been created! You are now able to log in with the username: ' + new_username, 'success')
            send_generate_username(form_register.email.data, new_username)
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)

# Generates a random 3 digit code. Returns a 3 character long string
def random_code():
    import random
    x=random.randint(000,999)
    if x<10:
        x= '0'+str(x)+'0'
    else:
        if x>=10 and x<100:
            x= '0'+str(x)

    return x

# Generates a username based on the users first name, last name, and a randomly generated 3 digit code
def generate_username(first_name, last_name, random):
	if len(first_name) > 8 and len(last_name)>8:
	  return first_name[0:8] + last_name[0:8] + str(random)
	else:
	  if len(first_name)>8:
	    return first_name[0:8] + last_name +str(random)
	  else:
	    if len(last_name)>8:
	      return first_name + last_name[0:8] +str(random)
	    else:
	      return first_name+last_name+str(random)

# Checks to see if the username is already taken. If it is, add 1 to the 3 digit code (it repeats this until it finds an unused code)
# It returns the original username if it is not taken, and returns the new username if it is taken
# If all 1000 possible usernames are taken, it will return 'ERRROR'
def check_username(first_last_rand, all_usernames):

    global match
    match = False
    new_username = first_last_rand

    # Check if username is taken
    for username in all_usernames:
        if username == first_last_rand:
            match = True
            break
            
    # If the username is taken, generate a new code
    if match:
        randnumberstring = new_username[(len(new_username) - 3):(len(new_username) + 1)]
        randnumber = int(randnumberstring)
        number_of_matches = 1
        
        # Add 1 to the 3 digit code until we find an unused code
        while match:
        
                # If we've tried every possible code, return 'ERROR'
                if number_of_matches == 1000:
                    return 'ERROR'
        
                # Loop back to 000 if the code is 999
                if randnumber == 999:
                    randnumberstring = '000'              
                # Otherwise add 1 to the code
                else:
                    randnumber = randnumber + 1
                    randnumberstring = str(randnumber)
                    if randnumber < 10:
                        randnumberstring = '00' + str(randnumber)
                    if (randnumber >= 10) and (randnumber < 100):
                        randnumberstring = '0' + str(randnumber)
                        
                #Create the new username
                new_username = (new_username[0:len(new_username) - 3]+ str(randnumberstring))
                match = False
                
                # Check to make sure the new username isn't already in use
                for username in all_usernames:
                    if username == new_username:
                        randnumber = int(randnumberstring)
                        match = True
                        number_of_matches += 1
                        break

    return new_username






@app.route("/login", methods=['GET', 'POST'])
def login():
    # Login Form Submitted
    form_register = RegistrationForm()
    form_login = LoginForm()
    if form_login.validate_on_submit():

        mysession = loadSession()
        user = mysession.query(User).filter(User.username == form_login.username.data).first()
       # user.last_login=datetime.now()
       # session.commit()
        if user and bcrypt.check_password_hash(user.password, form_login.password.data):
            login_user(user, remember=form_login.remember.data)
            next_page = request.args.get('next')
            user.last_login = datetime.now()
            mysession.commit()
            """
              MN:  use session to store username
            """
            session['myusername']=form_login.username.data
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    result = [row.badge_name for row in Badge.get_all_badges_names()]
    return render_template('dashboard.html', result=result)



@app.route("/logout")
def logout():

    logout_user()

    return redirect(url_for('landpage'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RequestResetForm()

    if form.validate_on_submit():
        session = loadSession()
        user = session.query(User).filter(User.email == form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('landpage'))

    return render_template('reset_request.html', title='Rest Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('landpage'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        #this is the new password that the user has chosen
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        print("Original: ", user.password)
        #updating the password requires first loading a new session 
        session = loadSession()
        #once a session is loaded we want to get the row 
        #where User.id matches the id of the user returned by User.verify_reset_token(token)
        #this insures that the password for the correct user will be the one changed
        row = session.query(User).filter(User.id==user.id).first()
        #Change the password is a simple assign statement
        row.password = hashed_password
        #Changes need to be committed in order to make it to the database
        session.commit()
        #send a message to the user telling them that there account has been updated successfully
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('landpage'))
    return render_template('reset_token.html', title='Rest Password', form=form)


@app.route("/reset_user", methods=['GET', 'POST'])
def reset_user():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RequestResetUserForm()

    if form.validate_on_submit():
        session = loadSession()
        user = session.query(User).filter(User.email == form.email.data).first()

        send_reset_user(user)
        flash('An email has been sent with your username.', 'info')
        return redirect(url_for('landpage'))

    return render_template('reset_user.html', title='Rest User', form=form)



def send_reset_user(user):
    msg = Message('User Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Hi '''+user.first_name+'''\n Your user name is ''' + user.username
    mail.send(msg)


def send_generate_username(useremail,username):
    msg = Message('Username Generation',
                  sender='noreply@demo.com',
                  recipients=[useremail])
    msg.body = f'''Thank you for registering an account with Oregon MESA your unique
username has been generated and it is '''+username+'''
please keep this email handy as you will need that username every time you
login to the app. '''
    mail.send(msg)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        session = loadSession()
        myaccount = session.query(User).filter(User.username == current_user.username).first()

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            myaccount.picture=picture_file
            myaccount.school = form.school.data

        session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':

        form.username.data = current_user.username
        form.email.data = current_user.email
        print(current_user.picture)
    image_file = url_for('static', filename='img/' + current_user.picture)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn