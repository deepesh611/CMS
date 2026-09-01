"""Previous church experience and service history before joining."""
from app.extensions import db
from app.models.base import TimestampMixin


class PreviousChurchExperience(TimestampMixin, db.Model):
    """Captures a member's service history at a prior church."""

    __tablename__ = "previous_church_experiences"

    id = db.Column("ExperienceID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID",
        db.Integer,
        db.ForeignKey("members.MemberID"),
        nullable=False,
    )

    # Church information
    church_name = db.Column("ChurchName", db.String(150), nullable=False)
    denomination = db.Column("Denomination", db.String(120))
    city = db.Column("City", db.String(120))
    country = db.Column("Country", db.String(80))

    # Service period
    service_start_date = db.Column("ServiceStartDate", db.Date)
    service_end_date = db.Column("ServiceEndDate", db.Date)

    # Leadership details
    leadership_role = db.Column("LeadershipRole", db.String(80))
    ministry_served = db.Column("MinistryServed", db.String(120))
    responsibilities = db.Column("Responsibilities", db.Text)
    total_duration = db.Column("TotalDuration", db.String(80))

    # Reference contact
    reference_contact = db.Column("ReferenceContact", db.String(120))
    reference_phone = db.Column("ReferencePhone", db.String(40))
    reference_email = db.Column("ReferenceEmail", db.String(120))

    member = db.relationship("Member", back_populates="previous_churches")

    ROLE_CHOICES = [
        "Pastor",
        "Associate Pastor",
        "Elder",
        "Deacon",
        "Ministry Leader",
        "Bible Teacher",
        "Worship Leader",
        "Youth Leader",
        "Coordinator",
        "Member",
    ]

    def __repr__(self):
        return f"<PreviousChurchExperience {self.church_name} member={self.member_id}>"
