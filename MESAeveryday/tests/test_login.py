import pytest

from MESAeveryday import app, bcrypt, mail

@pytest.fixture
def test_login():
    login_app = app()
    return login_app
