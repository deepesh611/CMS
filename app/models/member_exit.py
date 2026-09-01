"""Member exit, relocation, and church transfer management."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class MemberExit(TimestampMixin, db.Model):
    """Complete record of a departing member."""

    __tablename__ = "member_exits"

    id = db.Column("ExitID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID",
        db.Integer,
        db.ForeignKey("members.MemberID"),
        nullable=False,
    )

    # Exit details
    last_date_in_church = db.Column("LastDateInChurch", db.Date)
    exit_category = db.Column("ExitCategory", db.String(80), nullable=False)
    exit_reason = db.Column("ExitReason", db.Text)
    departure_notes = db.Column("DepartureNotes", db.Text)
    exit_date = db.Column("ExitDate", db.DateTime, default=utcnow)

    # Destination details
    dest_country = db.Column("DestCountry", db.String(80))
    dest_state = db.Column("DestState", db.String(120))
    dest_city = db.Column("DestCity", db.String(120))
    dest_address = db.Column("DestAddress", db.String(255))
    dest_postal_code = db.Column("DestPostalCode", db.String(20))

    # Employment information
    company_name = db.Column("CompanyName", db.String(150))
    company_position = db.Column("CompanyPosition", db.String(120))
    company_email = db.Column("CompanyEmail", db.String(120))
    company_contact = db.Column("CompanyContact", db.String(40))

    # New contact information
    new_mobile = db.Column("NewMobile", db.String(40))
    new_whatsapp = db.Column("NewWhatsApp", db.String(40))
    new_personal_email = db.Column("NewPersonalEmail", db.String(120))
    new_alternate_email = db.Column("NewAlternateEmail", db.String(120))

    # New church information
    new_church_name = db.Column("NewChurchName", db.String(150))
    new_church_address = db.Column("NewChurchAddress", db.String(255))
    new_pastor_name = db.Column("NewPastorName", db.String(120))
    new_pastor_contact = db.Column("NewPastorContact", db.String(40))
    new_pastor_email = db.Column("NewPastorEmail", db.String(120))

    # Future engagement
    willing_to_be_contacted = db.Column(
        "WillingToBeContacted", db.Boolean, default=True
    )
    preferred_communication = db.Column(
        "PreferredCommunication", db.String(40)
    )
    followup_frequency = db.Column("FollowupFrequency", db.String(40))

    # Emergency / home country contact
    emergency_contact_person = db.Column("EmergencyContactPerson", db.String(120))
    emergency_relationship = db.Column("EmergencyRelationship", db.String(80))
    emergency_mobile = db.Column("EmergencyMobile", db.String(40))
    emergency_whatsapp = db.Column("EmergencyWhatsApp", db.String(40))
    emergency_email = db.Column("EmergencyEmail", db.String(120))
    emergency_address = db.Column("EmergencyAddress", db.String(255))

    member = db.relationship("Member", back_populates="exit_record")

    EXIT_CATEGORIES = [
        "Relocation",
        "Employment Transfer",
        "Migration",
        "Family Relocation",
        "Education",
        "Church Transfer",
        "Personal Reasons",
        "Retirement",
        "Other",
    ]

    COMMUNICATION_METHODS = [
        "Phone",
        "WhatsApp",
        "Email",
        "SMS",
    ]

    FOLLOWUP_FREQUENCIES = [
        "Weekly",
        "Monthly",
        "Quarterly",
        "Annually",
        "No Follow-up",
    ]

    def __repr__(self):
        return f"<MemberExit member={self.member_id} category={self.exit_category}>"
