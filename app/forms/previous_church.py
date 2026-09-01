"""Forms for previous church experience."""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional

from app.models.previous_church import PreviousChurchExperience


class PreviousChurchForm(FlaskForm):
    """Capture prior church service history."""

    church_name = StringField("Church Name", validators=[DataRequired()])
    denomination = StringField("Denomination", validators=[Optional()])
    city = StringField("City", validators=[Optional()])
    country = StringField("Country", validators=[Optional()])

    service_start_date = DateField("Service Start Date", validators=[Optional()])
    service_end_date = DateField("Service End Date", validators=[Optional()])

    leadership_role = SelectField(
        "Leadership Role",
        choices=[("", "—")] + [(r, r) for r in PreviousChurchExperience.ROLE_CHOICES],
        default="",
        validators=[Optional()],
    )
    ministry_served = StringField("Ministry Served", validators=[Optional()])
    responsibilities = TextAreaField("Responsibilities", validators=[Optional()])
    total_duration = StringField("Total Duration", validators=[Optional()])

    reference_contact = StringField("Reference Contact", validators=[Optional()])
    reference_phone = StringField("Reference Phone", validators=[Optional()])
    reference_email = StringField("Reference Email", validators=[Optional(), Email()])
