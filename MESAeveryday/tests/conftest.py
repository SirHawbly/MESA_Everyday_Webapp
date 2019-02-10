"""
Pytests for removing stamps, current level, current accumulated points, and points needed for next level.
Using https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/
Written by Millen Wan
"""

import sys

# sys.path.insert(0, os.path.pardir)
sys.path.append('..')

import pytest
from flask_login import login_user, logout_user
from MESAeveryday import bcrypt, models, app

@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    flask_app.config['WTF_CSRF_METHODS'] = []

    test_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield test_client

    ctx.pop()

@pytest.fixture
def user():
    user = models.User.get_user_by_username("jsmith")
    return user

"""
class TestRemove(object):
    def test_rstamps(self):
        x = "this"
        assert 'h' in x

    def test_rclevel(self):
        x = "hello"
        assert hasattr(x, 'check')
"""