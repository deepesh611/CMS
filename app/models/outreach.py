"""Visitors, outreach programs, and follow-ups."""
from app.extensions import db
from app.models.base import TimestampMixin


class Visitor(TimestampMixin, db.Model):
    __tablename__ = "visitors"

    id = db.Column("VisitorID", db.Integer, primary_key=True)
    first_name = db.Column("FirstName", db.String(80), nullable=False)
    last_name = db.Column("LastName", db.String(80))
    phone = db.Column("Phone", db.String(40))
    email = db.Column("Email", db.String(120))
    address = db.Column("Address", db.String(255))
    visit_date = db.Column("VisitDate", db.Date, index=True)
    invited_by = db.Column("InvitedBy", db.String(120))
    prayer_requests = db.Column("PrayerRequests", db.Text)
    followup_status = db.Column("FollowupStatus", db.String(40), default="Pending")

    followups = db.relationship(
        "VisitorFollowup", back_populates="visitor", cascade="all, delete-orphan"
    )
    outreach_links = db.relationship(
        "OutreachVisitor", back_populates="visitor", cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return " ".join(p for p in [self.first_name, self.last_name] if p)


class VisitorFollowup(TimestampMixin, db.Model):
    __tablename__ = "visitor_followups"

    id = db.Column("FollowupID", db.Integer, primary_key=True)
    visitor_id = db.Column(
        "VisitorID", db.Integer, db.ForeignKey("visitors.VisitorID"), nullable=False
    )
    followup_date = db.Column("FollowupDate", db.Date)
    assigned_worker = db.Column("AssignedWorker", db.String(120))
    outcome = db.Column("Outcome", db.String(255))

    visitor = db.relationship("Visitor", back_populates="followups")


class OutreachProgram(TimestampMixin, db.Model):
    __tablename__ = "outreach_programs"

    id = db.Column("OutreachID", db.Integer, primary_key=True)
    name = db.Column("ProgramName", db.String(150), nullable=False)
    outreach_date = db.Column("OutreachDate", db.Date)
    location = db.Column("Location", db.String(150))
    organizers = db.Column("Organizers", db.String(255))
    team_members = db.Column("TeamMembers", db.Text)

    visitor_links = db.relationship(
        "OutreachVisitor", back_populates="program", cascade="all, delete-orphan"
    )


class OutreachVisitor(TimestampMixin, db.Model):
    __tablename__ = "outreach_visitors"

    id = db.Column("OutreachVisitorID", db.Integer, primary_key=True)
    outreach_id = db.Column(
        "OutreachID",
        db.Integer,
        db.ForeignKey("outreach_programs.OutreachID"),
        nullable=False,
    )
    visitor_id = db.Column(
        "VisitorID", db.Integer, db.ForeignKey("visitors.VisitorID"), nullable=False
    )
    followup_status = db.Column("FollowupStatus", db.String(40), default="Pending")

    program = db.relationship("OutreachProgram", back_populates="visitor_links")
    visitor = db.relationship("Visitor", back_populates="outreach_links")
