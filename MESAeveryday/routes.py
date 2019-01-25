"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask import render_template, url_for, flash, redirect, request
from MESAeveryday import app, bcrypt, mail
from MESAeveryday.forms import RegistrationForm, LoginForm, RequestResetForm, RequestResetUserForm, ResetPasswordForm, EarnStampsForm, UpdateEmailForm, UpdateNameForm, UpdateSchoolForm, UpdatePasswordForm
from MESAeveryday.models import User, School, Badge, Stamp, UserStamp, Avatar
from MESAeveryday.calendar_events import get_event_list, searchEvents
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from flask_mail import Message
from datetime import datetime
import secrets
import os

@app.route("/", methods=['GET', 'POST'])
@app.route("/landpage", methods=['GET', 'POST'])
def landpage():
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
        new_username = check_username(new_username, [row.username for row in User.get_all_username()])

        if new_username == 'ERROR':
            flash('Sorry, we were unable to generate an account for you.', 'danger')
        else:
            # Generate hashed password
            hashed_password = bcrypt.generate_password_hash(form_register.password.data).decode('utf-8')

            # Add user to the databas
            new_user = User(new_username, form_register.firstname.data, form_register.lastname.data,
                            form_register.email.data, hashed_password, form_register.school.data)
            User.add_new_user(new_user)

            # Tell the user their new username and send them an email with the username
            flash('Your account has been created! You are now able to log in with the username: ' + new_username, 'success')
            send_generate_username(form_register.email.data, new_username)

    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Login Form Submitted
    form_register = RegistrationForm()
    form_login = LoginForm()
    if form_login.validate_on_submit():
        user = User.get_user_by_username(form_login.username.data)
        if user and bcrypt.check_password_hash(user.password, form_login.password.data):
            User.update_last_login(user.id, datetime.now())
            login_user(user, remember=form_login.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('landpage.html', title='Landing', form_l=form_login, form_r=form_register)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # Added by Millen
    if (User.verify_role(current_user.id)):
        return redirect(url_for('admin'))
    # result = [row.badge_name for row in Badge.get_all_badges_names()]
    temp = Badge.get_all_badges_id_with_names()
    result, badges = [row.badge_name for row in temp], [row.badge_id for row in temp]
    # this block for viewing needed stamps
    id = current_user.id    # get the id of current user
    pts= []
    for badge in badges:
        points = [row.points for row in Stamp.get_earned_points(id, badge)]                  # get earned points of a badge
        pt = 0 if not points else sum(points)
        pts.append(pt)

    # # call the google api and pull all upcoming events
    events = get_event_list()
    # # parse the events into incoming and special groups
    mesa_days = searchEvents(events, ['Mesa','Day'])
    other_days = searchEvents(events, ['Mesa','Day'])
    upcoming_events = [event for event in events if event['remain_days'] < 7]

    return render_template('dashboard.html',
                           events=events,
                           number_upcoming=len(upcoming_events),
                           upcoming_events=upcoming_events,
                           result=zip(result, badges),
                           mesa_days=mesa_days,
                           other_days=other_days,
                           points=zip(result, pts))

# Added by Millen
# Load admin page if role is admin
@app.route("/admin")
@login_required
def admin():
    # https://stackoverflow.com/questions/21895839/restricting-access-to-certain-areas-of-a-flask-view-function-by-role
    if not User.verify_role(current_user.id):
        # flash('You do not have access to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route("/logout")
def logout():

    logout_user()

    return redirect(url_for('landpage'))


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data)
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
        # with loadSession() as session:
        #     #once a session is loaded we want to get the row
        #     #where User.id matches the id of the user returned by User.verify_reset_token(token)
        #     #this insures that the password for the correct user will be the one changed
        #     row = session.query(User).filter(User.id==user.id).first()
        #     #Change the password is a simple assign statement
        #     row.password = hashed_password
        #     #Changes need to be committed in order to make it to the database
        #     session.commit()
        # #send a message to the user telling them that there account has been updated successfully
        if User.reset_pwd(user.id, hashed_password) == True:
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('landpage'))
    return render_template('reset_token.html', title='Rest Password', form=form)


@app.route("/reset_user", methods=['GET', 'POST'])
def reset_user():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetUserForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data)
        send_reset_user(user)
        flash('An email has been sent with your username.', 'info')
        return redirect(url_for('landpage'))
    return render_template('reset_user.html', title='Rest User', form=form)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    emailform = UpdateEmailForm()
    nameform = UpdateNameForm()
    schoolform = UpdateSchoolForm()
    passwordform= UpdatePasswordForm()
    avatars = ""
    myaccount = User.get_user_by_username(current_user.username)

	#Update password
    if passwordform.password.data and passwordform.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(passwordform.password.data).decode('utf-8')
        if User.reset_pwd(myaccount.id, hashed_password) == True:
            flash('Your account has been successfully updated!', 'success')
        else:
            flash('Sorry, we were unable to update your account', 'danger')
        return redirect(url_for('account'))

	#Update email
    if emailform.email.data and emailform.validate_on_submit():
        if User.update_email(myaccount.id, emailform.email.data) == True:
            flash('Your account has been successfully updated!', 'success')
        else:
            flash('Sorry, we were unable to update your account', 'danger')
        return redirect(url_for('account'))

	#Update name
    if (nameform.firstname.data or nameform.lastname.data) and nameform.validate_on_submit():
        if User.update_name(myaccount.id, nameform.firstname.data, nameform.lastname.data) == True:
            flash('Your account has been successfully updated!', 'success')
        else:
            flash('Sorry, we were unable to update your account', 'danger')
        return redirect(url_for('account'))

    #Update school
    if schoolform.school.data and schoolform.validate_on_submit():
        if User.update_school(myaccount.id, schoolform.school.data) == True:
            flash('Your account has been successfully updated!', 'success')
        else:
            flash('Sorry, we were unable to update your account', 'danger')
        return redirect(url_for('account'))

    #Update avatar
    if request.method=='POST':
        avatarSelect = request.form.get('avatarSelect')
        if avatarSelect:
            if User.update_avatar(myaccount.id, avatarSelect) == True:
                flash('Your account has been successfully updated!', 'success')
            else:
                flash('Sorry, we were unable to update your account', 'danger')
            return redirect(url_for('account'))

    #Load page
    if request.method =='GET':
        emailform.email.data = current_user.email
        nameform.firstname.data = current_user.first_name
        nameform.lastname.data = current_user.last_name
        schoolform.school.data = current_user.school_id

    return render_template('account.html', title='Account', avatar_files=Avatar.get_all_avatars(), form_email=emailform, form_name=nameform, form_password=passwordform, form_school=schoolform)

@app.route("/earn_stamps", methods=['GET', 'POST'])
@login_required
def earn_stamps():
    result = [row.badge_name for row in Badge.get_all_badges_names()]                                   # maintain some objects in dashboard
    badges = {row.badge_id : row.badge_name for row in Badge.get_all_badges_id_with_names()}.items()    # a dictionary -> badge_id : badge_name
    forms, t = [], 1        # several pairs of forms (stamp, date, submit). t is used to assign unique id
    for badge in badges:
        stamps = Stamp.get_stamps_of_badge(badge[0])

        if stamps.first() is not None:
            form = EarnStampsForm(badge[1], prefix=badge[1])    # create a pair of form. prefix -> make each form unique

            form.time_finished.id = "date" + str(t)             # to create an unique id without space, slash, etc...
                                                                # HTML doesnt seem to be friendly to an id with space(s), sigh

            form.stamps.choices = stamps                      # assign unearned stamps to the select field
            forms.append(form)                                  # create a list of forms
            t += 1
    for form in forms:
        if form.submit.data:
            if form.validate_on_submit():
                id = current_user.id    # acquire the user_id of current user
                if UserStamp.earn_stamp(id, form.stamps.data, datetime.now(), form.time_finished.data.strftime('%Y-%m-%d')) == True:
                    # flash('You've earned a new stamp!', 'success')
                    # some message should be shown here, flash doesnt work
                    print('successfully added.')
                # else:
                    # flash('Failed adding stamp', 'warning')
                    # some message should be shown here, flash doesnt work
                return redirect('/dashboard')   # could be redirected to either dashboard or the same page?
    return render_template('earnstamps.html', title='Earn Stamps', forms=forms, result=result)

@app.route("/badges/<badgeid>", methods=['GET', 'POST'])
@login_required
def check_badge(badgeid):
    temp = Badge.get_all_badges_id_with_names()
    result, ids = [row.badge_name for row in temp], [row.badge_id for row in temp]
    badge_name = Badge.get_badge_name(badgeid).first()[0]
    picture_file = Badge.get_badge_picture(badgeid).first()[0]
    id = current_user.id    # get the id of current user
    unearned_stamps = [row.stamp_name for row in Stamp.get_unearned_stamps_of_badge(id, badgeid)]   # the unearned stamps of current user
    earned_stamps = [row.stamp_name for row in Stamp.get_earned_stamps_of_badge(id, badgeid)]
    if not unearned_stamps:
        unearned_stamps = ['All stamps earned'] # if all the stamps for this badge have been earned, print this instead
    points = [row.points for row in Stamp.get_earned_points(id, badgeid)]
    pt = 0 if not points else sum(points)
    current_level, to_next_lv = Badge.get_level_related_info(badgeid, pt)
    return render_template('badges.html', result=zip(result, ids), badge_name=badge_name, unearned=unearned_stamps, earned=earned_stamps, pt=pt, lv=current_level, to_next_lv=to_next_lv, picture_file=picture_file)

# Generates a random 3 digit code. Returns the code as a 3 character long string
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

#Sends a link to the user for resetting their password
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

#Sends the username of a user. Used when I user selects "Forgot Username"

def send_reset_user(user):
    msg = Message('User Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Hi '''+user.first_name+'''\nYour username is ''' + user.username
    mail.send(msg)


#Sends the username generate to an account. This email sent only after registration
def send_generate_username(useremail,username):
    msg = Message('Username Generation',
                  sender='noreply@demo.com',
                  recipients=[useremail])
    msg.body = f'''Thank you for registering an account with Oregon MESA your unique
username has been generated and it is '''+username+'''
please keep this email handy as you will need that username every time you
login to the app. '''
    mail.send(msg)
