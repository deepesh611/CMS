"""Tithes, offerings, donations, missions, mission support, welfare."""
from app.extensions import db
from app.models.base import TimestampMixin


class Tithe(TimestampMixin, db.Model):
    __tablename__ = "tithes"

    id = db.Column("TitheID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    amount = db.Column("Amount", db.Numeric(12, 2), nullable=False)
    payment_date = db.Column("PaymentDate", db.Date, index=True)
    payment_method = db.Column("PaymentMethod", db.String(40))

    member = db.relationship("Member")


class Offering(TimestampMixin, db.Model):
    __tablename__ = "offerings"

    id = db.Column("OfferingID", db.Integer, primary_key=True)
    amount = db.Column("Amount", db.Numeric(12, 2), nullable=False)
    service_date = db.Column("ServiceDate", db.Date, index=True)
    service_type = db.Column("ServiceType", db.String(80))


class Donation(TimestampMixin, db.Model):
    __tablename__ = "donations"

    id = db.Column("DonationID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    donor_name = db.Column("DonorName", db.String(120))
    amount = db.Column("Amount", db.Numeric(12, 2), nullable=False)
    purpose = db.Column("Purpose", db.String(150))
    donation_date = db.Column("DonationDate", db.Date, index=True)

    member = db.relationship("Member")


class Mission(TimestampMixin, db.Model):
    __tablename__ = "missions"

    id = db.Column("MissionID", db.Integer, primary_key=True)
    name = db.Column("MissionName", db.String(150), nullable=False)
    country = db.Column("Country", db.String(80))
    mission_type = db.Column("MissionType", db.String(40))  # Local/Overseas

    supports = db.relationship(
        "MissionSupport", back_populates="mission", cascade="all, delete-orphan"
    )


class MissionSupport(TimestampMixin, db.Model):
    __tablename__ = "mission_support"

    id = db.Column("SupportID", db.Integer, primary_key=True)
    mission_id = db.Column(
        "MissionID", db.Integer, db.ForeignKey("missions.MissionID"), nullable=False
    )
    amount = db.Column("Amount", db.Numeric(12, 2), nullable=False)
    support_date = db.Column("SupportDate", db.Date, index=True)

    mission = db.relationship("Mission", back_populates="supports")


class WelfareRequest(TimestampMixin, db.Model):
    __tablename__ = "welfare_requests"

    id = db.Column("WelfareID", db.Integer, primary_key=True)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    support_type = db.Column("SupportType", db.String(80))
    amount = db.Column("Amount", db.Numeric(12, 2))
    status = db.Column("Status", db.String(40), default="Submitted")
    approved_by = db.Column("ApprovedBy", db.String(120))
    followup_actions = db.Column("FollowupActions", db.Text)

    member = db.relationship("Member")
