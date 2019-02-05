import pytest
from MESAeveryday import app

# # Sign Out
# # some information on things to test in the signout
# # tests.
# #   - No Personal Info should be released?
# #   - Logged in user should be reset to none

def test_username(app):
    return app

# # run all of the tests having to do with logging out
@pytest.fixture
def test_logout():
    logout_app = app()

    test_username(logout_app)

    return logout_app