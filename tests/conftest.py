import pytest
from MESAeveryday import bcrypt, app, models
from flask_login import login_user, logout_user

@pytest.fixture(scope='module')
def test_client():
    flask_app = app

    # flask_app.config['WTF_CSRF_METHODS'] = []
    flask_app.config['WTF_CSRF_ENABLED'] = False

    test_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()
    yield test_client
    ctx.pop()