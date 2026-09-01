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
    join_date = db.Column("JoinDate", db.Date)
    appointment_date = db.Column("AppointmentDate", db.Date)
    active_flag = db.Column("ActiveFlag", db.Boolean, default=True)
    status = db.Column("Status", db.String(40), default="Active")

    ministry = db.relationship("Ministry", back_populates="ministry_members")
    member = db.relationship("Member")

    ROLE_CHOICES = [
        "Volunteer",
        "Coordinator",
        "Assistant Leader",
        "Ministry Leader",
        "Department Head",
        "Pastor",
        "Elder",
        "Deacon",
    ]


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
    end_date = db.Column("EndDate", db.Date)
    active_status = db.Column("ActiveStatus", db.Boolean, default=True)
    department = db.Column("Department", db.String(120))
    responsibilities = db.Column("Responsibilities", db.Text)
    term_duration = db.Column("TermDuration", db.String(80))
    reporting_to = db.Column("ReportingTo", db.String(120))
    leadership_level = db.Column("LeadershipLevel", db.String(80))

    member = db.relationship("Member")
    role = db.relationship("LeadershipRole", back_populates="member_leaderships")


class MinistryMovement(TimestampMixin, db.Model):
    """Historical record of ministry transfers, promotions, and exits."""

    __tablename__ = "ministry_movements"

    id = db.Column("MovementID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    movement_type = db.Column("MovementType", db.String(40), nullable=False)

    # Previous
    previous_ministry_id = db.Column(
        "PreviousMinistryID", db.Integer, db.ForeignKey("ministries.MinistryID")
    )
    previous_role = db.Column("PreviousRole", db.String(80))

    # New
    new_ministry_id = db.Column(
        "NewMinistryID", db.Integer, db.ForeignKey("ministries.MinistryID")
    )
    new_role = db.Column("NewRole", db.String(80))

    effective_date = db.Column("EffectiveDate", db.Date, nullable=False)
    last_date_previous = db.Column("LastDatePrevious", db.Date)
    reason = db.Column("Reason", db.Text)
    approved_by = db.Column("ApprovedBy", db.String(120))
    notes = db.Column("Notes", db.Text)

    member = db.relationship("Member", back_populates="ministry_movements")
    previous_ministry = db.relationship("Ministry", foreign_keys=[previous_ministry_id])
    new_ministry = db.relationship("Ministry", foreign_keys=[new_ministry_id])

    MOVEMENT_TYPES = [
        "New Assignment",
        "Transfer",
        "Promotion",
        "Leadership Appointment",
        "Leadership Exit",
        "Temporary Assignment",
        "Resignation",
        "Retirement",
        "Suspension",
        "Ministry Exit",
    ]

    def __repr__(self):
        return f"<MinistryMovement {self.movement_type} member={self.member_id}>"
