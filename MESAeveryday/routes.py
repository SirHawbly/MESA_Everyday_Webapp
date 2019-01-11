"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import render_template, url_for, flash, redirect, request,session
from MESAeveryday import app, bcrypt, mail
from MESAeveryday.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,RequestResetUserForm,UpdateAccountForm,UpdateSchoolForm,UpdatePasswordForm
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
        hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')
        new_user = User(form_register.username.data, form_register.firstname.data, form_register.lastname.data,
                        form_register.email.data, hashed_password, form_register.school.data)

        session = loadSession()
        session.add(new_user)
        session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('landpage'))

    else:

        newusername=combinename(form_register.firstname.data,form_register.lastname.data,random())
        result = [row.username for row in User.get_all_username()]
        print(result)
        newusername=checkfirstlastrand(newusername,result)
        hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')
        new_user = User(newusername, form_register.firstname.data, form_register.lastname.data,
                        form_register.email.data, hashed_password, form_register.school.data)
        session = loadSession()
        session.add(new_user)
        session.commit()
        flash('Your account has been created! You are now able to log in with username:'+newusername, 'success')

        send_generate_username(form_register.email.data,newusername)
        return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)

def random():
    import random
    x=random.randint(000,999)
    if x<10:
        x= '0'+str(x)+'0'
    else:
        if x>=10 and x<100:
            x= '0'+str(x)

    return x
def combinename(first_name,last_name,random):
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

def checkfirstlastrand(first_last_rand,arr):

    global match
    match=False

    for item in arr:
        if item == first_last_rand:
            match = True
            break
    if not match:
        return first_last_rand
    else :
        randnumber = int(first_last_rand[(len(first_last_rand) - 3):(len(first_last_rand) + 1)])
        randnumberstring = first_last_rand[(len(first_last_rand) - 3):(len(first_last_rand) + 1)]
        while match:
			#randnumber = int(first_last_rand[(len(first_last_rand) - 3):(len(first_last_rand) + 1)])
			#randnumberstring = first_last_rand[(len(first_last_rand) - 3):(len(first_last_rand) + 1)]

                if randnumber == 999:
                    randnumberstring = '000'
                else:
                    randnumber = randnumber + 1
                    randnumberstring = str(randnumber)
                    if randnumber < 10:
                        randnumberstring = '00' + str(randnumber)
                    if (randnumber >= 10) and (randnumber < 100):
                        randnumberstring = '0' + str(randnumber)
                match=False
                for item1 in arr:

                    if item1==(first_last_rand[0:len(first_last_rand) - 3]+str(randnumberstring)):
                        randnumber= int(randnumberstring)
                        match=True
                        break

        return (first_last_rand[0:len(first_last_rand) - 3]+ str(randnumberstring))






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
    schoolform = UpdateSchoolForm()
    passwordform= UpdatePasswordForm()

    if request.method=='POST':

        if 'email' in request.form:

        #if form.validate_on_submit():
            session = loadSession()
            myaccount = session.query(User).filter(User.username == current_user.username).first()
            myaccount.email=form.email.data
            myaccount.first_name=form.firstname.data
            myaccount.last_name=form.lastname.data


            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                myaccount.picture=picture_file
            session.commit()
            print(myaccount.email)
            print(myaccount.picture)
           # flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        elif 'school' in request.form:
            session = loadSession()
            myaccount = session.query(User).filter(User.username == current_user.username).first()
            myaccount.schoolid = schoolform.school.data
            print(schoolform.school.data)
            session.commit()

            return redirect(url_for('account'))
        elif 'password' in request.form:
            session = loadSession()
            myaccount = session.query(User).filter(User.username == current_user.username).first()
            hashed_password = bcrypt.generate_password_hash(passwordform.password.data).decode('utf-8')
            myaccount.password = hashed_password
            session.commit()


    elif request.method =='GET':

        form.email.data = current_user.email
        form.firstname.data=current_user.first_name
        form.lastname.data=current_user.last_name



    image_file = url_for('static', filename='img/' + current_user.picture)
    print(image_file)

    return render_template('account.html', title='Account', image_file=image_file, form=form)


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