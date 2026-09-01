"""Discipleship 4-level tracking and ministry eligibility."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class DiscipleshipProgress(TimestampMixin, db.Model):
    """Tracks a member's completion of the four discipleship levels."""

    __tablename__ = "discipleship_progress"

    id = db.Column("ProgressID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID",
        db.Integer,
        db.ForeignKey("members.MemberID"),
        nullable=False,
        unique=True,
    )

    # Level 1
    level1_status = db.Column(
        "Level1Status", db.String(40), default="Not Started"
    )
    level1_completion_date = db.Column("Level1CompletionDate", db.Date)

    # Level 2
    level2_status = db.Column(
        "Level2Status", db.String(40), default="Not Started"
    )
    level2_completion_date = db.Column("Level2CompletionDate", db.Date)

    # Level 3
    level3_status = db.Column(
        "Level3Status", db.String(40), default="Not Started"
    )
    level3_completion_date = db.Column("Level3CompletionDate", db.Date)

    # Level 4
    level4_status = db.Column(
        "Level4Status", db.String(40), default="Not Started"
    )
    level4_completion_date = db.Column("Level4CompletionDate", db.Date)

    # Metadata
    facilitator = db.Column("Facilitator", db.String(120))
    remarks = db.Column("Remarks", db.Text)
    certificate_number = db.Column("CertificateNumber", db.String(80))
    certificate_path = db.Column("CertificatePath", db.String(255))

    member = db.relationship("Member", back_populates="discipleship_progress")

    @property
    def is_all_completed(self):
        """True when all four discipleship levels are marked Completed."""
        return all(
            s == "Completed"
            for s in [
                self.level1_status,
                self.level2_status,
                self.level3_status,
                self.level4_status,
            ]
        )

    @property
    def completed_levels(self):
        """Number of levels completed (0–4)."""
        return sum(
            1
            for s in [
                self.level1_status,
                self.level2_status,
                self.level3_status,
                self.level4_status,
            ]
            if s == "Completed"
        )

    def __repr__(self):
        return f"<DiscipleshipProgress member={self.member_id} levels={self.completed_levels}/4>"


class EligibilityOverride(TimestampMixin, db.Model):
    """Admin override allowing ministry enrollment before completing all levels."""

    __tablename__ = "eligibility_overrides"

    id = db.Column("OverrideID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID",
        db.Integer,
        db.ForeignKey("members.MemberID"),
        nullable=False,
    )
    override_reason = db.Column("OverrideReason", db.Text, nullable=False)
    approved_by_user_id = db.Column(
        "ApprovedByUserID", db.Integer, db.ForeignKey("users.UserID"), nullable=False
    )
    override_date = db.Column("OverrideDate", db.DateTime, default=utcnow)
    is_active = db.Column("IsActive", db.Boolean, default=True)

    member = db.relationship("Member", back_populates="eligibility_overrides")
    approved_by = db.relationship("User")

    def __repr__(self):
        return f"<EligibilityOverride member={self.member_id} active={self.is_active}>"
