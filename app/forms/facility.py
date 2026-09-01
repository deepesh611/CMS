"""Forms for room, facility, and booking management."""
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Email, NumberRange, Optional

from app.models.facility import Room, RoomBooking


class BuildingForm(FlaskForm):
    """Add or edit a building."""

    name = StringField("Building Name", validators=[DataRequired()])
    address = StringField("Address", validators=[Optional()])
    contact_person = StringField("Contact Person", validators=[Optional()])
    contact_phone = StringField("Contact Phone", validators=[Optional()])


class RoomForm(FlaskForm):
    """Add or edit a room within a building."""

    building_id = SelectField("Building", coerce=int, validators=[DataRequired()])
    name = StringField("Room Name", validators=[DataRequired()])
    floor = StringField("Floor", validators=[Optional()])
    capacity = IntegerField("Capacity", validators=[Optional(), NumberRange(min=0)])
    room_type = SelectField(
        "Room Type",
        choices=[("", "—")] + [(t, t) for t in Room.ROOM_TYPES],
        validators=[Optional()],
    )
    rental_rate = DecimalField(
        "Rental Rate", places=2, default=0, validators=[Optional()]
    )
    deposit_amount = DecimalField(
        "Deposit Amount", places=2, default=0, validators=[Optional()]
    )
    status = SelectField(
        "Status",
        choices=[(s, s) for s in Room.STATUS_CHOICES],
        default="Available",
    )


class ExternalChurchForm(FlaskForm):
    """Register a partner church for facility sharing."""

    name = StringField("Church Name", validators=[DataRequired()])
    contact_person = StringField("Contact Person", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    email = StringField("Email", validators=[Optional(), Email()])
    address = StringField("Address", validators=[Optional()])


class RoomBookingForm(FlaskForm):
    """Book a room for an event."""

    room_id = SelectField("Room", coerce=int, validators=[DataRequired()])
    requesting_church_id = SelectField(
        "Requesting Church", coerce=int, validators=[Optional()]
    )
    ministry = StringField("Ministry", validators=[Optional()])
    event_name = StringField("Event Name", validators=[DataRequired()])
    event_type = StringField("Event Type", validators=[Optional()])
    expected_attendance = IntegerField(
        "Expected Attendance", validators=[Optional(), NumberRange(min=0)]
    )
    notes = TextAreaField("Notes", validators=[Optional()])
    recurrence = SelectField(
        "Recurrence",
        choices=[(r, r) for r in RoomBooking.RECURRENCE_CHOICES],
        default="One Time",
    )
    booking_status = SelectField(
        "Booking Status",
        choices=[(s, s) for s in RoomBooking.BOOKING_STATUS_CHOICES],
        default="Pending",
    )

    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    num_participants = IntegerField(
        "Number of Participants", validators=[Optional(), NumberRange(min=0)]
    )

    rental_amount = DecimalField(
        "Rental Amount", places=2, default=0, validators=[Optional()]
    )
    security_deposit = DecimalField(
        "Security Deposit", places=2, default=0, validators=[Optional()]
    )
    discount = DecimalField(
        "Discount", places=2, default=0, validators=[Optional()]
    )
    taxes = DecimalField(
        "Taxes", places=2, default=0, validators=[Optional()]
    )
    payment_status = SelectField(
        "Payment Status",
        choices=[(s, s) for s in RoomBooking.PAYMENT_STATUS_CHOICES],
        default="Pending",
    )
