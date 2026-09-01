"""Room, facility, and booking management."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class Building(TimestampMixin, db.Model):
    """Church building or facility."""

    __tablename__ = "buildings"

    id = db.Column("BuildingID", db.Integer, primary_key=True)
    name = db.Column("BuildingName", db.String(120), nullable=False)
    address = db.Column("Address", db.String(255))
    contact_person = db.Column("ContactPerson", db.String(120))
    contact_phone = db.Column("ContactPhone", db.String(40))

    rooms = db.relationship(
        "Room", back_populates="building", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Building {self.name}>"


class Room(TimestampMixin, db.Model):
    """Individual room within a building."""

    __tablename__ = "rooms"

    id = db.Column("RoomID", db.Integer, primary_key=True)
    building_id = db.Column(
        "BuildingID",
        db.Integer,
        db.ForeignKey("buildings.BuildingID"),
        nullable=False,
    )
    name = db.Column("RoomName", db.String(120), nullable=False)
    floor = db.Column("Floor", db.String(40))
    capacity = db.Column("Capacity", db.Integer)
    room_type = db.Column("RoomType", db.String(80))
    rental_rate = db.Column("RentalRate", db.Numeric(10, 2), default=0)
    deposit_amount = db.Column("DepositAmount", db.Numeric(10, 2), default=0)
    status = db.Column("Status", db.String(40), default="Available")

    building = db.relationship("Building", back_populates="rooms")
    bookings = db.relationship(
        "RoomBooking", back_populates="room", cascade="all, delete-orphan"
    )

    ROOM_TYPES = [
        "Sanctuary",
        "Auditorium",
        "Classroom",
        "Meeting Room",
        "Prayer Hall",
        "Fellowship Hall",
        "Training Room",
        "Counseling Room",
        "Youth Room",
        "Children's Room",
    ]

    STATUS_CHOICES = ["Available", "Occupied", "Maintenance", "Reserved"]

    def __repr__(self):
        return f"<Room {self.name} ({self.room_type})>"


class ExternalChurch(TimestampMixin, db.Model):
    """Partner church that may share facilities."""

    __tablename__ = "external_churches"

    id = db.Column("ExternalChurchID", db.Integer, primary_key=True)
    name = db.Column("ChurchName", db.String(150), nullable=False)
    contact_person = db.Column("ContactPerson", db.String(120))
    phone = db.Column("Phone", db.String(40))
    email = db.Column("Email", db.String(120))
    address = db.Column("Address", db.String(255))

    bookings = db.relationship("RoomBooking", back_populates="requesting_church")

    def __repr__(self):
        return f"<ExternalChurch {self.name}>"


class RoomBooking(TimestampMixin, db.Model):
    """Room booking / reservation record."""

    __tablename__ = "room_bookings"

    id = db.Column("BookingID", db.Integer, primary_key=True)
    booking_number = db.Column(
        "BookingNumber", db.String(40), unique=True, index=True
    )
    room_id = db.Column(
        "RoomID",
        db.Integer,
        db.ForeignKey("rooms.RoomID"),
        nullable=False,
    )
    requesting_church_id = db.Column(
        "RequestingChurchID",
        db.Integer,
        db.ForeignKey("external_churches.ExternalChurchID"),
    )

    # Event details
    ministry = db.Column("Ministry", db.String(120))
    event_name = db.Column("EventName", db.String(150), nullable=False)
    event_type = db.Column("EventType", db.String(80))
    recurrence = db.Column("Recurrence", db.String(40), default="One Time")

    # Schedule
    start_date = db.Column("StartDate", db.Date, nullable=False, index=True)
    end_date = db.Column("EndDate", db.Date, nullable=False)
    start_time = db.Column("StartTime", db.Time, nullable=False)
    end_time = db.Column("EndTime", db.Time, nullable=False)
    num_participants = db.Column("NumParticipants", db.Integer)

    # Financial
    rental_amount = db.Column("RentalAmount", db.Numeric(10, 2), default=0)
    security_deposit = db.Column("SecurityDeposit", db.Numeric(10, 2), default=0)
    discount = db.Column("Discount", db.Numeric(10, 2), default=0)
    taxes = db.Column("Taxes", db.Numeric(10, 2), default=0)
    final_charge = db.Column("FinalCharge", db.Numeric(10, 2), default=0)
    invoice_number = db.Column("InvoiceNumber", db.String(40))
    payment_status = db.Column("PaymentStatus", db.String(40), default="Pending")

    # Status
    booking_status = db.Column("BookingStatus", db.String(40), default="Confirmed")

    room = db.relationship("Room", back_populates="bookings")
    requesting_church = db.relationship("ExternalChurch", back_populates="bookings")

    RECURRENCE_CHOICES = [
        "One Time",
        "Daily",
        "Weekly",
        "Monthly",
        "Quarterly",
        "Yearly",
    ]

    PAYMENT_STATUS_CHOICES = [
        "Pending",
        "Partial",
        "Paid",
        "Refunded",
        "Waived",
    ]

    BOOKING_STATUS_CHOICES = [
        "Confirmed",
        "Tentative",
        "Cancelled",
        "Completed",
    ]

    @staticmethod
    def generate_booking_number():
        """Generate the next booking number in sequence."""
        last = RoomBooking.query.order_by(RoomBooking.id.desc()).first()
        n = (last.id + 1) if last else 1
        return f"BKG-{n:05d}"

    @staticmethod
    def check_conflict(room_id, start_date, end_date, start_time, end_time, exclude_id=None):
        """Check for overlapping bookings on the same room."""
        query = RoomBooking.query.filter(
            RoomBooking.room_id == room_id,
            RoomBooking.booking_status != "Cancelled",
            RoomBooking.start_date <= end_date,
            RoomBooking.end_date >= start_date,
            RoomBooking.start_time < end_time,
            RoomBooking.end_time > start_time,
        )
        if exclude_id:
            query = query.filter(RoomBooking.id != exclude_id)
        return query.all()

    def __repr__(self):
        return f"<RoomBooking {self.booking_number} {self.event_name}>"
