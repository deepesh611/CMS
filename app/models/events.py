"""Events, sermons, pastors, event assignments, and attendance."""
from app.extensions import db
from app.models.base import TimestampMixin


class Event(TimestampMixin, db.Model):
    __tablename__ = "events"

    id = db.Column("EventID", db.Integer, primary_key=True)
    name = db.Column("EventName", db.String(150), nullable=False)
    event_type = db.Column("EventType", db.String(80))  # Daily/Weekly/Conference/...
    event_date = db.Column("EventDate", db.Date, index=True)
    location = db.Column("Location", db.String(150))
    notes = db.Column("Notes", db.Text)

    sermons = db.relationship("Sermon", back_populates="event", cascade="all, delete-orphan")
    assignments = db.relationship(
        "EventAssignment", back_populates="event", cascade="all, delete-orphan"
    )
    attendance = db.relationship(
        "Attendance", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Event {self.name} {self.event_date}>"


class Pastor(TimestampMixin, db.Model):
    __tablename__ = "pastors"

    id = db.Column("PastorID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    position = db.Column("Position", db.String(120))

    member = db.relationship("Member")
    sermons = db.relationship("Sermon", back_populates="pastor")


class Sermon(TimestampMixin, db.Model):
    __tablename__ = "sermons"

    id = db.Column("SermonID", db.Integer, primary_key=True)
    event_id = db.Column("EventID", db.Integer, db.ForeignKey("events.EventID"))
    pastor_id = db.Column("PastorID", db.Integer, db.ForeignKey("pastors.PastorID"))
    title = db.Column("SermonTitle", db.String(200), nullable=False)
    scripture_reference = db.Column("ScriptureReference", db.String(200))
    service_date = db.Column("ServiceDate", db.Date, index=True)
    service_type = db.Column("ServiceType", db.String(80))
    notes = db.Column("Notes", db.Text)

    event = db.relationship("Event", back_populates="sermons")
    pastor = db.relationship("Pastor", back_populates="sermons")


class EventAssignment(TimestampMixin, db.Model):
    __tablename__ = "event_assignments"

    id = db.Column("AssignmentID", db.Integer, primary_key=True)
    event_id = db.Column(
        "EventID", db.Integer, db.ForeignKey("events.EventID"), nullable=False
    )
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    assigned_role = db.Column("AssignedRole", db.String(80))

    event = db.relationship("Event", back_populates="assignments")
    member = db.relationship("Member")


class Attendance(TimestampMixin, db.Model):
    __tablename__ = "attendance"

    id = db.Column("AttendanceID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    event_id = db.Column("EventID", db.Integer, db.ForeignKey("events.EventID"))
    attendance_date = db.Column("AttendanceDate", db.Date, index=True)
    status = db.Column("Status", db.String(20), default="Present")  # Present/Absent
    check_in_time = db.Column("CheckInTime", db.Time)
    notes = db.Column("Notes", db.String(255))

    member = db.relationship("Member")
    event = db.relationship("Event", back_populates="attendance")
