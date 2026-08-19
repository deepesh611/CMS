"""Prayer requests, counselling cases, follow-ups, and baby dedications."""
from app.extensions import db
from app.models.base import TimestampMixin


class PrayerRequest(TimestampMixin, db.Model):
    __tablename__ = "prayer_requests"

    id = db.Column("PrayerRequestID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    request_details = db.Column("RequestDetails", db.Text, nullable=False)
    category = db.Column("Category", db.String(80))
    assigned_team = db.Column("AssignedTeam", db.String(120))
    status = db.Column("Status", db.String(40), default="Open")  # Open/Answered/Withdrawn
    testimony = db.Column("Testimony", db.Text)

    member = db.relationship("Member")


class CounsellingCase(TimestampMixin, db.Model):
    __tablename__ = "counselling_cases"

    id = db.Column("CaseID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    counsellor_id = db.Column(
        "CounsellorID", db.Integer, db.ForeignKey("members.MemberID")
    )
    case_type = db.Column("CaseType", db.String(80))
    session_date = db.Column("SessionDate", db.Date)
    summary = db.Column("Summary", db.Text)
    confidential_notes = db.Column("ConfidentialNotes", db.Text)
    status = db.Column("Status", db.String(40), default="Open")

    member = db.relationship("Member", foreign_keys=[member_id])
    counsellor = db.relationship("Member", foreign_keys=[counsellor_id])
    followups = db.relationship(
        "CounsellingFollowup", back_populates="case", cascade="all, delete-orphan"
    )


class CounsellingFollowup(TimestampMixin, db.Model):
    __tablename__ = "counselling_followups"

    id = db.Column("FollowupID", db.Integer, primary_key=True)
    case_id = db.Column(
        "CaseID", db.Integer, db.ForeignKey("counselling_cases.CaseID"), nullable=False
    )
    followup_date = db.Column("FollowupDate", db.Date)
    assigned_counsellor_id = db.Column(
        "AssignedCounsellorID", db.Integer, db.ForeignKey("members.MemberID")
    )
    reminder = db.Column("Reminder", db.Boolean, default=False)
    notes = db.Column("Notes", db.Text)

    case = db.relationship("CounsellingCase", back_populates="followups")
    assigned_counsellor = db.relationship("Member")


class BabyDedication(TimestampMixin, db.Model):
    __tablename__ = "baby_dedications"

    id = db.Column("DedicationID", db.Integer, primary_key=True)
    child_id = db.Column("ChildID", db.Integer, db.ForeignKey("children.ChildID"))
    dedication_date = db.Column("DedicationDate", db.Date)
    pastor_id = db.Column("PastorID", db.Integer, db.ForeignKey("pastors.PastorID"))
    certificate_issued = db.Column("CertificateIssued", db.Boolean, default=False)

    child = db.relationship("Child")
    pastor = db.relationship("Pastor")
