"""Care cells, ministries, and leadership structures."""
from app.extensions import db
from app.models.base import TimestampMixin


class CareCell(TimestampMixin, db.Model):
    __tablename__ = "care_cells"

    id = db.Column("CareCellID", db.Integer, primary_key=True)
    name = db.Column("CareCellName", db.String(120), nullable=False)
    # use_alter breaks the members <-> care_cells FK cycle so DDL ordering
    # works on every backend (Postgres/MySQL create the FK via ALTER after
    # both tables exist).
    leader_id = db.Column(
        "LeaderID",
        db.Integer,
        db.ForeignKey("members.MemberID", use_alter=True, name="fk_carecell_leader"),
    )
    assistant_leader_id = db.Column(
        "AssistantLeaderID",
        db.Integer,
        db.ForeignKey(
            "members.MemberID", use_alter=True, name="fk_carecell_assistant"
        ),
    )
    location = db.Column("Location", db.String(255))
    meeting_schedule = db.Column("MeetingSchedule", db.String(255))

    leader = db.relationship("Member", foreign_keys=[leader_id])
    assistant_leader = db.relationship("Member", foreign_keys=[assistant_leader_id])
    direct_members = db.relationship(
        "Member",
        foreign_keys="Member.care_cell_id",
        back_populates="care_cell",
    )
    cell_members = db.relationship(
        "CareCellMember", back_populates="care_cell", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CareCell {self.name}>"


class CareCellMember(TimestampMixin, db.Model):
    __tablename__ = "carecell_members"

    id = db.Column("CellMemberID", db.Integer, primary_key=True)
    care_cell_id = db.Column(
        "CareCellID", db.Integer, db.ForeignKey("care_cells.CareCellID"), nullable=False
    )
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )

    care_cell = db.relationship("CareCell", back_populates="cell_members")
    member = db.relationship("Member")


class Ministry(TimestampMixin, db.Model):
    __tablename__ = "ministries"

    id = db.Column("MinistryID", db.Integer, primary_key=True)
    name = db.Column("MinistryName", db.String(120), nullable=False)
    description = db.Column("Description", db.String(255))

    ministry_members = db.relationship(
        "MinistryMember", back_populates="ministry", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ministry {self.name}>"


class MinistryMember(TimestampMixin, db.Model):
    __tablename__ = "ministry_members"

    id = db.Column("MinistryMemberID", db.Integer, primary_key=True)
    ministry_id = db.Column(
        "MinistryID", db.Integer, db.ForeignKey("ministries.MinistryID"), nullable=False
    )
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    ministry_role = db.Column("MinistryRole", db.String(80))

    ministry = db.relationship("Ministry", back_populates="ministry_members")
    member = db.relationship("Member")


class LeadershipRole(TimestampMixin, db.Model):
    __tablename__ = "leadership_roles"

    id = db.Column("LeadershipRoleID", db.Integer, primary_key=True)
    name = db.Column("RoleName", db.String(120), nullable=False)

    member_leaderships = db.relationship(
        "MemberLeadership", back_populates="role", cascade="all, delete-orphan"
    )


class MemberLeadership(TimestampMixin, db.Model):
    __tablename__ = "member_leadership"

    id = db.Column("EntryID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    leadership_role_id = db.Column(
        "LeadershipRoleID",
        db.Integer,
        db.ForeignKey("leadership_roles.LeadershipRoleID"),
        nullable=False,
    )
    appointment_date = db.Column("AppointmentDate", db.Date)
    department = db.Column("Department", db.String(120))
    responsibilities = db.Column("Responsibilities", db.Text)
    term_duration = db.Column("TermDuration", db.String(80))

    member = db.relationship("Member")
    role = db.relationship("LeadershipRole", back_populates="member_leaderships")
