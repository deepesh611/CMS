"""Ordination management for ordained ministers."""
from app.extensions import db
from app.models.base import TimestampMixin


class Ordination(TimestampMixin, db.Model):
    """Pastoral ordination information for a member."""

    __tablename__ = "ordinations"

    id = db.Column("OrdinationID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID",
        db.Integer,
        db.ForeignKey("members.MemberID"),
        nullable=False,
        unique=True,
    )

    is_ordained = db.Column("IsOrdained", db.Boolean, default=False)
    ordination_date = db.Column("OrdinationDate", db.Date)
    ordaining_church = db.Column("OrdainingChurch", db.String(150))
    ordaining_organization = db.Column("OrdainingOrganization", db.String(150))
    ordaining_authority = db.Column("OrdainingAuthority", db.String(150))
    certificate_number = db.Column("CertificateNumber", db.String(80))
    certificate_path = db.Column("CertificatePath", db.String(255))
    remarks = db.Column("Remarks", db.Text)

    member = db.relationship("Member", back_populates="ordination")

    def __repr__(self):
        status = "Ordained" if self.is_ordained else "Not Ordained"
        return f"<Ordination member={self.member_id} {status}>"
