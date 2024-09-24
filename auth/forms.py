from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import Email, ValidationError, Length, EqualTo, DataRequired
import re


'''character_check is uses reg-expression to forbid certain characters from being entered in specific fields'''


def character_check(form, field):
    excluding = "*?!'@^+=/[]{}()#$£<>"
    for char in field.data:
        if char in excluding:
            raise ValidationError(f"Character {char} is not allowed.")
            # Raises this error message when regex is not matched.


'''validate_phone ensures an entered phone number is 11 digits long.'''


def validate_phone(form, field):
    p = re.compile(r'\d{11}')
    if not p.match(field.data):
        raise ValidationError("Enter 11 digit UK phone number (starts with 0).")
        # Raises this error message when regex is not matched.


'''validate_password forces password fields to contain at least 1 digit, 1 lowercase and uppercase character,
 1 special character.'''


def validate_password(form, field):
    p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
    if not p.match(field.data):
        raise ValidationError(
            'Password must contain at least 1 digit, 1 lowercase and uppercase character, 1 special character.')
        # Raises this error message when regex is not matched.


'''Each field within the following forms uses DataRequired to ensure none of the fields are empty.'''


'''Register form contains the fields required for the register() view function in auth/views.'''


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired(), character_check])
    email = EmailField(validators=[DataRequired(), Email()])  # EmailField forces input to be email format
    phone = StringField(validators=[DataRequired(), validate_phone])  # Validate_phone called on this field
    password = PasswordField(validators=[
        DataRequired(), validate_password, Length(min=8, message='Password must be at least 8 characters')])
    # Add minimum length of 8 to passwords and calls validate_password on this field.
    confirm_password = PasswordField(
        validators=[DataRequired(), EqualTo('password', message='Passwords must be equal')])
    # checks that passwords match
    submit = SubmitField('Register')


'''Login form contains the fields needed for the login view function in auth/views.
It requires a user name and password.'''


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log In')
