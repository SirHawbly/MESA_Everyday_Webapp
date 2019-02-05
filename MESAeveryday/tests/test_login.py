import pytest
from MESAeveryday import app, bcrypt, mail
from MESAeveryday.models import User

# # Sign In 
# # items shouldnt need to be tested for validity, they should already be 
# # vetted by registering
# #   - Name - just needs to match an account, should be valid 
# #   - Password - just needs to match the account, should be valid
# #   - Account - should be the account owned by the inputted name
# #   - Logged In User - Logging in should open the correct account
# #   - Logged In User - This account should also be pulled correctly


# # test the user's name when logging in
def test_username(app, username, password):
    return app.post('/login', user=[username, password], follow_redirects=True)
    

# # run all of the tests having to do with logging in
@pytest.fixture
def test_login():
    login_app = app()

    test_username(login_app, "asdf", "asdf")

    return login_app
