"""Forms for member exit, relocation, and church transfer."""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Optional

from app.models.member_exit import MemberExit


class MemberExitForm(FlaskForm):
    """Multi-section form for processing a member's departure."""

    # Exit details
    last_date_in_church = DateField("Last Date in Church", validators=[Optional()])
    exit_category = SelectField(
        "Exit Category",
        choices=[("", "— Select —")] + [(c, c) for c in MemberExit.EXIT_CATEGORIES],
        validators=[DataRequired()],
    )
    exit_reason = TextAreaField("Exit Reason", validators=[Optional()])
    departure_notes = TextAreaField("Departure Notes", validators=[Optional()])

    # Destination
    dest_country = StringField("Destination Country", validators=[Optional()])
    dest_state = StringField("Destination State", validators=[Optional()])
    dest_city = StringField("Destination City", validators=[Optional()])
    dest_address = StringField("Destination Address", validators=[Optional()])
    dest_postal_code = StringField("Postal Code", validators=[Optional()])

    # Employment
    company_name = StringField("Company Name", validators=[Optional()])
    company_position = StringField("Position", validators=[Optional()])
    company_email = StringField("Company Email", validators=[Optional(), Email()])
    company_contact = StringField("Company Contact", validators=[Optional()])

    # New contact
    new_mobile = StringField("New Mobile", validators=[Optional()])
    new_whatsapp = StringField("New WhatsApp", validators=[Optional()])
    new_personal_email = StringField(
        "New Personal Email", validators=[Optional(), Email()]
    )
    new_alternate_email = StringField(
        "New Alternate Email", validators=[Optional(), Email()]
    )

    # New church
    new_church_name = StringField("New Church Name", validators=[Optional()])
    new_church_address = StringField("New Church Address", validators=[Optional()])
    new_pastor_name = StringField("Pastor Name", validators=[Optional()])
    new_pastor_contact = StringField("Pastor Contact", validators=[Optional()])
    new_pastor_email = StringField(
        "Pastor Email", validators=[Optional(), Email()]
    )

    # Future engagement
    willing_to_be_contacted = BooleanField("Willing to Be Contacted", default=True)
    preferred_communication = SelectField(
        "Preferred Communication",
        choices=[("", "—")] + [(m, m) for m in MemberExit.COMMUNICATION_METHODS],
        validators=[Optional()],
    )
    followup_frequency = SelectField(
        "Follow-up Frequency",
        choices=[("", "—")] + [(f, f) for f in MemberExit.FOLLOWUP_FREQUENCIES],
        validators=[Optional()],
    )

    # Emergency contact
    emergency_contact_person = StringField(
        "Emergency Contact Person", validators=[Optional()]
    )
    emergency_relationship = StringField("Relationship", validators=[Optional()])
    emergency_mobile = StringField("Emergency Mobile", validators=[Optional()])
    emergency_whatsapp = StringField("Emergency WhatsApp", validators=[Optional()])
    emergency_email = StringField(
        "Emergency Email", validators=[Optional(), Email()]
    )
    emergency_address = StringField("Emergency Address", validators=[Optional()])
