from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Optional

FOLLOWUP_STATUS = [
    ("Pending", "Pending"),
    ("Contacted", "Contacted"),
    ("Converted", "Converted"),
    ("Closed", "Closed"),
]


class OutreachProgramForm(FlaskForm):
    name = StringField("Program Name", validators=[DataRequired(), Length(max=150)])
    outreach_date = DateField("Date", validators=[Optional()])
    location = StringField("Venue", validators=[Optional(), Length(max=150)])
    organizers = StringField("Organizers", validators=[Optional(), Length(max=255)])
    team_members = TextAreaField("Team Members", validators=[Optional()])
    submit = SubmitField("Save")


class VisitorForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=80)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    visit_date = DateField("Visit Date", validators=[Optional()])
    invited_by = StringField("Invited By", validators=[Optional(), Length(max=120)])
    prayer_requests = TextAreaField("Prayer Requests", validators=[Optional()])
    followup_status = SelectField("Follow-Up Status", choices=FOLLOWUP_STATUS)
    submit = SubmitField("Save")


class FollowupForm(FlaskForm):
    followup_date = DateField("Follow-Up Date", validators=[Optional()])
    assigned_worker = StringField(
        "Assigned Worker", validators=[Optional(), Length(max=120)]
    )
    outcome = StringField("Outcome", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add Follow-Up")
