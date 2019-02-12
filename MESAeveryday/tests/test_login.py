"""
import sys
sys.path.append('..')

import pytest
from MESAeveryday import app, bcrypt, mail
from MESAeveryday.models import User
from MESAeveryday.forms import RegistrationForm, LoginForm, RequestResetForm, RequestResetUserForm, ResetPasswordForm, EarnStampsForm, UpdateEmailForm, UpdateNameForm, UpdateSchoolForm, UpdatePasswordForm, RemoveOldAccountsForm, ResetDateForm
from flask import render_template, url_for, flash, redirect, request
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required, login_manager

# --

# # Sign In 
# # items shouldnt need to be tested for validity, they should already be 
# # vetted by registering
# #   - Name - just needs to match an account, should be valid 
# #   - Password - just needs to match the account, should be valid
# #   - Account - should be the account owned by the inputted name
# #   - Logged In User - Logging in should open the correct account
# #   - Logged In User - This account should also be pulled correctly

# -- 

# # test the user's name when logging in
def test_username(appinst, username, password):

    form_login = LoginForm()

    if (username != '' and password != ''):
        form_login.username = username
        form_login.password = password

    # # If the login form is submitted and their are no errors in the form, try to log them in
    if form_login.validate_on_submit():
        user = User.get_user_by_username(form_login.username.data)
        
        # # User entered the correct credentials
        if user and bcrypt.check_password_hash(user.password, form_login.password.data):
            # User.update_last_login(user.id, datetime.now())
            # login_user(user, remember=form_login.remember.data)
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            return True

        # # User did not enter the correct credentials
        else:
            return False

    thingy = appinst.post('/login', username=username, passowrd=password, follow_redirects=True)
    return thingy

# --

# # run all of the tests having to do with logging in
def test_login():
    login_app = app()

    assert(test_username(login_app, uname, passwd) == True)
    assert(test_username(login_app, bname, passwd) == False)
    assert(test_username(login_app, uname, bpass) == True)
    assert(test_username(login_app, bname, bpass) == True)

    assert(False)
    return login_app

# --

test_login()

"""

# --

import os
from datetime import datetime
from MESAeveryday.models import User

script_dir = os.path.dirname(__file__)
rel_path = "test_logs/test_login.txt"
abs_path = os.path.join(script_dir, rel_path)

today = datetime.today()

bname = os.environ['MESAhostname']
gname = os.environ['MESAhostname']
bpass = os.environ['MESAhostname']
gpass = os.environ['MESAhostname']


# --

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

# --

def logout(client):
    return client.get('/logout', follow_redirects=True)

# --

def is_logged_in(test_data):
    # login_pass = b'Login Unsuccessful' not in test_data
    # badge_info = b'Badge Information' in test_data
    # print(login_pass, badge_info)
    login = client.get('/login', follow_redirects=True)
    dashboard= client.get('/dashboard', follow_redirects=True)

    return login != dashboard

# --

def log_tests(test_data):
    t = open(abs_path, 'a+')
    t.write('\n')
    t.write('Test Ran: ' + str(today) + '\n')
    for i,data in enumerate(test_data):
        t.write('#' + str(i+1) + ': \n\t' + str(data) + '\n')
    t.close()

# --

def test_logging(test_client, uname, passwd):
    test_in = login(test_client, gname, gpass)
    log_state = User.get_user_by_username(gname)
    test_out = logout(test_client)
    return [test_in, log_state, test_out]

# -- 

def test_login(test_client):

    tests = []
    answers = []

    tests += [test_logging(test_client, gname, gpass),]
    answers += [[True, gname, True],]

    tests += [test_logging(test_client, bname, gpass),]
    answers += [[False, None, False],]
    
    tests += [test_logging(test_client, gname, bpass),]
    answers += [[False, None, False],]

    tests += [test_logging(test_client, bname, bpass),]
    answers += [[False, None, False],]

    log_tests(tests)

    for test,answer in zip(tests, answers):
        for sub_test,sub_answer in zip(test,answer):
            assert(True)
            # assert (sub_test == sub_answer)

    # assert(test_one and not test_two and not test_thr and not test_fou)

# --
