"""Forms for ordination management."""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional


class OrdinationForm(FlaskForm):
    """Capture pastoral ordination information."""

    is_ordained = BooleanField("Ordained Pastor")
    ordination_date = DateField("Ordination Date", validators=[Optional()])
    ordaining_church = StringField("Ordaining Church", validators=[Optional()])
    ordaining_organization = StringField(
        "Ordaining Organization", validators=[Optional()]
    )
    ordaining_authority = StringField(
        "Ordaining Authority", validators=[Optional()]
    )
    certificate_number = StringField("Certificate Number", validators=[Optional()])
    remarks = TextAreaField("Remarks", validators=[Optional()])
