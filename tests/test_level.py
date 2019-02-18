import os
import pytest
import re
from MESAeveryday import bcrypt, models
from flask_login import login_user
from datetime import datetime

# use this to login an account
def login_account(client):
    username = "natsu"
    pwd = "a@123456"

    with client:
        response = client.post('/login', data=dict(username=username, password=pwd, submit="Login"), follow_redirects=True)
    return response

# check responsed HTML code
def write_response(filename, response):
    t = open(filename, 'w')
    t.write(str(response.data))
    t.close

# this passed -> login functional!
def test_login(test_client):
    response = login_account(test_client)

    # CHECK response html to make sure it gets redirected to dashboard
    write_response("login.txt", response)

    assert response.status_code == 200

# here's a way to test 4 different badge pages
@pytest.mark.parametrize(('url', 'filename'), [('/badges/1', 'badge1'), ('/badges/2', 'badge2'), ('/badges/3', 'badge3'), ('/badges/4', 'badge4')])
def test_level_adding(test_client, url, filename):
    login_account(test_client)
    earned_date = datetime.strptime('2019-2-14', '%Y-%m-%d').date()

    response = test_client.get(url, follow_redirects=True)
    write_response(filename, response)

    assert response.status_code == 200