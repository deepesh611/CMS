from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class InventoryItemForm(FlaskForm):
    asset_code = StringField("Asset Code", validators=[Optional(), Length(max=80)])
    asset_name = StringField("Asset Name", validators=[DataRequired(), Length(max=150)])
    category = SelectField(
        "Category",
        choices=[
            ("Instrument", "Instrument"),
            ("Computer", "Computer"),
            ("Audio Equipment", "Audio Equipment"),
            ("Projector", "Projector"),
            ("Furniture", "Furniture"),
            ("Vehicle", "Vehicle"),
            ("Other", "Other"),
        ],
    )
    value = DecimalField("Value / Cost", validators=[Optional(), NumberRange(min=0)], places=2)
    purchase_date = DateField("Purchase Date", validators=[Optional()])
    assigned_to = StringField("Assigned To", validators=[Optional(), Length(max=120)])
    status = SelectField(
        "Status",
        choices=[
            ("Active", "Active"),
            ("In Repair", "In Repair"),
            ("Retired", "Retired"),
            ("Lost", "Lost"),
        ],
    )
    next_maintenance_date = DateField("Next Maintenance", validators=[Optional()])
    submit = SubmitField("Save")


class MaintenanceLogForm(FlaskForm):
    service_date = DateField("Service Date", validators=[Optional()])
    remarks = TextAreaField("Remarks", validators=[Optional()])
    submit = SubmitField("Add Log")
