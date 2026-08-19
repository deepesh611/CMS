from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class CounsellingCaseForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[Optional()])
    counsellor_id = SelectField("Counsellor", coerce=int, validators=[Optional()])
    case_type = StringField("Case Type", validators=[Optional(), Length(max=80)])
    session_date = DateField("Session Date", validators=[Optional()])
    summary = TextAreaField("Summary", validators=[Optional()])
    confidential_notes = TextAreaField("Confidential Notes", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[("Open", "Open"), ("In Progress", "In Progress"), ("Closed", "Closed")],
    )
    submit = SubmitField("Save")


class CounsellingFollowupForm(FlaskForm):
    followup_date = DateField("Follow-Up Date", validators=[Optional()])
    assigned_counsellor_id = SelectField(
        "Assigned Counsellor", coerce=int, validators=[Optional()]
    )
    reminder = BooleanField("Set Reminder")
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Add Follow-Up")


class PrayerRequestForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[Optional()])
    request_details = TextAreaField("Request Details", validators=[DataRequired()])
    category = StringField("Category", validators=[Optional(), Length(max=80)])
    assigned_team = StringField("Assigned Prayer Team", validators=[Optional(), Length(max=120)])
    status = SelectField(
        "Status",
        choices=[("Open", "Open"), ("Answered", "Answered"), ("Withdrawn", "Withdrawn")],
    )
    testimony = TextAreaField("Testimony", validators=[Optional()])
    submit = SubmitField("Save")


class BabyDedicationForm(FlaskForm):
    child_id = SelectField("Child", coerce=int, validators=[DataRequired()])
    dedication_date = DateField("Dedication Date", validators=[Optional()])
    pastor_id = SelectField("Officiating Pastor", coerce=int, validators=[Optional()])
    certificate_issued = BooleanField("Certificate Issued")
    submit = SubmitField("Save")


class WelfareRequestForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[DataRequired()])
    support_type = StringField("Support Type", validators=[Optional(), Length(max=80)])
    amount = DecimalField(
        "Amount", validators=[Optional(), NumberRange(min=0)], places=2
    )
    status = SelectField(
        "Status",
        choices=[
            ("Submitted", "Submitted"),
            ("Under Review", "Under Review"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Closed", "Closed"),
        ],
    )
    approved_by = StringField("Approved By", validators=[Optional(), Length(max=120)])
    followup_actions = TextAreaField("Follow-Up Actions", validators=[Optional()])
    submit = SubmitField("Save")
