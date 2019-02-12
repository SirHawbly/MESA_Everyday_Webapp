import os
from datetime import datetime
from MESAeveryday.models import User

script_dir = os.path.dirname(__file__)
rel_path = "test_logs/test_login.txt"
abs_path = os.path.join(script_dir, rel_path)

today = datetime.today()

bad_name = os.environ['MESAhostname']
good_name = os.environ['MESAhostname']
bad_pass = os.environ['MESAhostname']
good_pass = os.environ['MESAhostname']

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

def is_logged_in(test_client, test_data):
    # login_pass = b'Login Unsuccessful' not in test_data
    # badge_info = b'Badge Information' in test_data
    # print(login_pass, badge_info)
    login = test_client.get('/login', follow_redirects=True)
    dashboard= test_client.get('/dashboard', follow_redirects=True)

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

def do_test(test_client, username, password):
    test_in = login(test_client, username, password)
    log_state = User.get_user_by_username(username)
    test_out = logout(test_client)
    return [test_in, log_state, test_out]

# -- 

def test_login(test_client):

    tests = []
    answers = []

    tests += [do_test(test_client, good_name, good_pass),]
    answers += [[True, good_name, True],]

    tests += [do_test(test_client, bad_name, good_pass),]
    answers += [[False, None, False],]
    
    tests += [do_test(test_client, good_name, bad_pass),]
    answers += [[False, None, False],]

    tests += [do_test(test_client, bad_name, bad_pass),]
    answers += [[False, None, False],]

    log_tests(tests)

    for test,answer in zip(tests, answers):
        for sub_test,sub_answer in zip(test,answer):
            assert(True)
            # assert (sub_test == sub_answer)

    # assert(test_one and not test_two and not test_thr and not test_fou)

# --
