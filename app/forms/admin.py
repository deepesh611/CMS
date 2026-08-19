from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role_id = SelectField("Role", coerce=int, validators=[DataRequired()])
    password = PasswordField(
        "Password", validators=[Optional(), Length(min=8)]
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")


class RoleForm(FlaskForm):
    name = StringField("Role Name", validators=[DataRequired(), Length(max=80)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save")
