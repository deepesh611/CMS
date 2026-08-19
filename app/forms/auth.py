from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class TwoFactorForm(FlaskForm):
    token = StringField(
        "Authentication Code", validators=[DataRequired(), Length(min=6, max=6)]
    )
    submit = SubmitField("Verify")


class Enable2FAForm(FlaskForm):
    token = StringField(
        "Authentication Code", validators=[DataRequired(), Length(min=6, max=6)]
    )
    submit = SubmitField("Enable 2FA")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8)]
    )
    submit = SubmitField("Change Password")
