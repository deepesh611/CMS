"""Forms for discipleship tracking and eligibility override."""
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Optional


_LEVEL_CHOICES = [
    ("Not Started", "Not Started"),
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
]


class DiscipleshipProgressForm(FlaskForm):
    """Track a member's completion of the 4 discipleship levels."""

    level1_status = SelectField(
        "Level 1 Status", choices=_LEVEL_CHOICES, default="Not Started"
    )
    level1_completion_date = DateField("Level 1 Completion Date", validators=[Optional()])

    level2_status = SelectField(
        "Level 2 Status", choices=_LEVEL_CHOICES, default="Not Started"
    )
    level2_completion_date = DateField("Level 2 Completion Date", validators=[Optional()])

    level3_status = SelectField(
        "Level 3 Status", choices=_LEVEL_CHOICES, default="Not Started"
    )
    level3_completion_date = DateField("Level 3 Completion Date", validators=[Optional()])

    level4_status = SelectField(
        "Level 4 Status", choices=_LEVEL_CHOICES, default="Not Started"
    )
    level4_completion_date = DateField("Level 4 Completion Date", validators=[Optional()])

    facilitator = StringField("Training Facilitator", validators=[Optional()])
    remarks = TextAreaField("Remarks", validators=[Optional()])
    certificate_number = StringField("Certificate Number", validators=[Optional()])


class EligibilityOverrideForm(FlaskForm):
    """Admin override for ministry eligibility."""

    override_reason = TextAreaField("Override Reason", validators=[DataRequired()])
