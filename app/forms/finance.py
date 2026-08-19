from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

PAYMENT_METHODS = [
    ("Cash", "Cash"),
    ("Bank Transfer", "Bank Transfer"),
    ("Card", "Card"),
    ("Mobile Money", "Mobile Money"),
    ("Cheque", "Cheque"),
]


class TitheForm(FlaskForm):
    member_id = SelectField("Member", coerce=int, validators=[Optional()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    payment_date = DateField("Payment Date", validators=[Optional()])
    payment_method = SelectField("Payment Method", choices=PAYMENT_METHODS)
    submit = SubmitField("Save")


class OfferingForm(FlaskForm):
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    service_date = DateField("Service Date", validators=[Optional()])
    service_type = StringField("Service Type", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Save")


class DonationForm(FlaskForm):
    member_id = SelectField("Member (optional)", coerce=int, validators=[Optional()])
    donor_name = StringField("Donor Name", validators=[Optional(), Length(max=120)])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    purpose = StringField("Purpose", validators=[Optional(), Length(max=150)])
    donation_date = DateField("Date", validators=[Optional()])
    submit = SubmitField("Save")


class MissionForm(FlaskForm):
    name = StringField("Mission Name", validators=[DataRequired(), Length(max=150)])
    country = StringField("Country", validators=[Optional(), Length(max=80)])
    mission_type = SelectField(
        "Type", choices=[("Local", "Local"), ("Overseas", "Overseas")]
    )
    submit = SubmitField("Save")


class MissionSupportForm(FlaskForm):
    mission_id = SelectField("Mission", coerce=int, validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    support_date = DateField("Support Date", validators=[Optional()])
    submit = SubmitField("Add Support")
