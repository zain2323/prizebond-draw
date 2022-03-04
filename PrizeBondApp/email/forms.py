from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError

def check_slash(form, field):
    if "/" in field.data:
        raise ValidationError("\ is not allowed.")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Email field can not be empty!"),
                                            Length(min=5, max=30), Email(), check_slash])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(message="Password field can not be empty!"),
                                                Length(min=8, max=60, message="Password length should be atleast 8 characters!"), check_slash])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Confirm password field can not be empty!"),
                                                EqualTo('password', message="Password mismatch"), check_slash])
    submit = SubmitField('Reset password')