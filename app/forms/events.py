from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional

EVENT_TYPES = [
    ("Sunday Service", "Sunday Service"),
    ("Daily Service", "Daily Service"),
    ("Weekly Service", "Weekly Service"),
    ("Monthly Service", "Monthly Service"),
    ("Bible Study", "Bible Study"),
    ("Prayer Meeting", "Prayer Meeting"),
    ("Conference", "Conference"),
    ("Outreach Event", "Outreach Event"),
    ("Other", "Other"),
]


class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired(), Length(max=150)])
    event_type = SelectField("Event Type", choices=EVENT_TYPES)
    event_date = DateField("Event Date", validators=[Optional()])
    location = StringField("Location", validators=[Optional(), Length(max=150)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save")


class SermonForm(FlaskForm):
    title = StringField("Sermon Title", validators=[DataRequired(), Length(max=200)])
    scripture_reference = StringField(
        "Scripture Reference", validators=[Optional(), Length(max=200)]
    )
    pastor_id = SelectField("Speaker", coerce=int, validators=[Optional()])
    service_date = DateField("Service Date", validators=[Optional()])
    service_type = StringField("Service Type", validators=[Optional(), Length(max=80)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save Sermon")


class AssignmentForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[DataRequired()])
    assigned_role = SelectField(
        "Role",
        choices=[
            ("Pastor", "Pastor"),
            ("Elder", "Elder"),
            ("Worship Leader", "Worship Leader"),
            ("Choir", "Choir"),
            ("Technician", "Technician"),
            ("Usher", "Usher"),
            ("Other", "Other"),
        ],
    )
    submit = SubmitField("Assign")
