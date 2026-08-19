from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

CHANNELS = [
    ("Email", "Email"),
    ("SMS", "SMS"),
    ("WhatsApp", "WhatsApp"),
    ("Facebook", "Facebook"),
    ("Telegram", "Telegram"),
    ("Instagram", "Instagram"),
    ("YouTube", "YouTube"),
]

CATEGORIES = [
    ("Announcement", "Church Announcement"),
    ("Devotion", "Daily Devotion"),
    ("Prayer", "Prayer Request"),
    ("Event", "Event Notification"),
    ("Birthday", "Birthday Greeting"),
    ("Anniversary", "Anniversary Greeting"),
]

RECIPIENT_GROUPS = [
    ("all", "All Members"),
    ("email", "Members with Email"),
    ("phone", "Members with Phone"),
]


class CommunicationForm(FlaskForm):
    channel = SelectField("Channel", choices=CHANNELS)
    category = SelectField("Category", choices=CATEGORIES)
    subject = StringField("Subject", validators=[Optional(), Length(max=200)])
    body = TextAreaField("Message", validators=[DataRequired()])
    recipient_group = SelectField("Recipients", choices=RECIPIENT_GROUPS)
    flyer = FileField(
        "Flyer (optional)",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only.")],
    )
    submit = SubmitField("Save Draft")
