from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class MinistryForm(FlaskForm):
    name = StringField("Ministry Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Save")


class CareCellForm(FlaskForm):
    name = StringField("Cell Name", validators=[DataRequired(), Length(max=120)])
    leader_id = SelectField("Leader", coerce=int, validators=[Optional()])
    assistant_leader_id = SelectField(
        "Assistant Leader", coerce=int, validators=[Optional()]
    )
    location = StringField("Meeting Location", validators=[Optional(), Length(max=255)])
    meeting_schedule = StringField(
        "Meeting Schedule", validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField("Save")


class MinistryMemberForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[DataRequired()])
    ministry_role = StringField("Role", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Add")


class LeadershipForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[DataRequired()])
    leadership_role_id = SelectField(
        "Leadership Role", coerce=int, validators=[DataRequired()]
    )
    appointment_date = DateField("Appointment Date", validators=[Optional()])
    department = StringField("Department", validators=[Optional(), Length(max=120)])
    responsibilities = TextAreaField("Responsibilities", validators=[Optional()])
    term_duration = StringField("Term Duration", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Save")
