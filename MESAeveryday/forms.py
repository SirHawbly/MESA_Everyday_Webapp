"""
Modified from CoreyMSchafer's Flask Tutorial
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/06-Login-Auth/flaskblog/routes.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from MESAeveryday.models import User, School, loadSession

class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    school = SelectField('School', coerce=int, choices=School.get_all_schools_names())
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="your password must be at least %(min)d characters")
                                 , Regexp("^(?=.*[0-9])(?=.*[!@#\$%\^&\*])",
                                          message="The string must contain at least 1 numeric digit and 1 symbol")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        session = loadSession()
        user = session.query(User).filter(User.username == username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        session = loadSession()
        user = session.query(User).filter(User.email == email.data).first()
        if user:
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
        session = loadSession()
        user = session.query(User).filter(User.email == email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must regiester first.')


class RequestResetUserForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request User Reset')

    def validate_email(self, email):
        session = loadSession()
        user = session.query(User).filter(User.email == email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must regiester first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',  validators=[DataRequired(), Length(min=8, message="your password must be at least %(min)d characters")
                                 , Regexp("^(?=.*[0-9])(?=.*[!@#\$%\^&\*])",
                                          message="The string must contain at least 1 numeric digit and 1 symbol")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
