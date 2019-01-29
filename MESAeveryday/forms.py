"""
This file contains all the forms used throughout the application
The application uses the flask_wtf library for creating forms
Each class only needs to describe what fields are in the form and how the fields should be validated

Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from MESAeveryday.models import User, School, Badge, Stamp
from flask_login import current_user
from MESAeveryday import bcrypt

class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    school = SelectField('School', coerce=int, choices=School.get_all_schools_names())
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="your password must be at least %(min)d characters")
                                 , Regexp("^(?=.*[0-9])(?=.*[!@#\$%\^&\*])",
                                          message="The string must contain at least 1 numeric digit and 1 symbol")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if User.get_user_by_email(email.data):
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.validate_email(email)
        if user == False:
            raise ValidationError('There is no account with that email. You must regester first.')

class RequestResetUserForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request User Reset')

    def validate_email(self, email):
        user = User.validate_email(email)
        if user == False:
            raise ValidationError('There is no account with that email. You must regester first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',  validators=[DataRequired(), Length(min=8, message="your password must be at least %(min)d characters")
                                 , Regexp("^(?=.*[0-9])(?=.*[!@#\$%\^&\*])",
                                          message="The string must contain at least 1 numeric digit and 1 symbol")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UpdateEmailForm(FlaskForm):

    email = StringField('Email', validators=[Email()])
	
    submit = SubmitField('Update Email')
    
    def validate_email(self, email):
        if User.get_user_by_email(email.data):
            raise ValidationError('That email is taken. Please choose a different one.')

class UpdateNameForm(FlaskForm):

    firstname = StringField('Firstname')
    lastname = StringField('Lastname')

    submit = SubmitField('Update Name')

class UpdateSchoolForm(FlaskForm):

    school = SelectField('School', coerce=int, choices=School.get_all_schools_names())

    submit = SubmitField('Update School')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Password')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8,
                                                                            message="your password must be at least %(min)d characters")
        , Regexp("^(?=.*[0-9])(?=.*[!@#\$%\^&\*])",
                 message="The string must contain at least 1 numeric digit and 1 symbol")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')
    
    def validate_old_password(self, old_password):

        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError('Old password is not correct.')

class EarnStampsForm(FlaskForm):
    stamps = SelectField('Stamp', coerce=int)
    time_finished = DateField('time finished', format='%m/%d/%Y', validators=[DataRequired()])
    submit = SubmitField('earn stamp')
    def __init__(self, badge_name, *args, **kwargs):
        super(EarnStampsForm, self).__init__(*args, **kwargs)
        self.badge_name = badge_name
