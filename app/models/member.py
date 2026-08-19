"""Members, spouses, children, photos, and documents."""
from datetime import date

from app.extensions import db
from app.models.base import TimestampMixin


def _calc_age(dob):
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class Member(TimestampMixin, db.Model):
    __tablename__ = "members"

    id = db.Column("MemberID", db.Integer, primary_key=True)
    member_number = db.Column("MemberNumber", db.String(40), unique=True, index=True)

    # Personal
    first_name = db.Column("FirstName", db.String(80), nullable=False)
    middle_name = db.Column("MiddleName", db.String(80))
    last_name = db.Column("LastName", db.String(80), nullable=False)
    dob = db.Column("DOB", db.Date)
    gender = db.Column("Gender", db.String(20))
    nationality = db.Column("Nationality", db.String(80))
    marital_status = db.Column("MaritalStatus", db.String(20))

    # Contact
    email = db.Column("Email", db.String(120))
    personal_email = db.Column("PersonalEmail", db.String(120))
    gsm_number = db.Column("GSMNumber", db.String(40))
    whatsapp_number = db.Column("WhatsAppNumber", db.String(40))
    address = db.Column("Address", db.String(255))

    # Employment
    employed = db.Column("Employed", db.Boolean, default=False)
    occupation = db.Column("Occupation", db.String(120))
    employer_name = db.Column("EmployerName", db.String(120))
    place_of_work = db.Column("PlaceOfWork", db.String(120))
    professional_category = db.Column("ProfessionalCategory", db.String(80))

    # Church details
    baptism_date = db.Column("BaptismDate", db.Date)
    joining_date = db.Column("JoiningDate", db.Date)
    membership_status = db.Column("MembershipStatus", db.String(40), default="Active")
    new_member_status = db.Column("NewMemberStatus", db.Boolean, default=True)
    welfare_required = db.Column("WelfareRequired", db.Boolean, default=False)

    # Previous / mother church
    mother_church_name = db.Column("MotherChurchName", db.String(120))
    mother_church_address = db.Column("MotherChurchAddress", db.String(255))
    mother_church_country = db.Column("MotherChurchCountry", db.String(80))

    care_cell_id = db.Column(
        "CareCellID", db.Integer, db.ForeignKey("care_cells.CareCellID")
    )

    # Relationships
    care_cell = db.relationship(
        "CareCell", foreign_keys=[care_cell_id], back_populates="direct_members"
    )
    spouse = db.relationship(
        "Spouse", back_populates="member", uselist=False, cascade="all, delete-orphan"
    )
    children = db.relationship(
        "Child", back_populates="member", cascade="all, delete-orphan"
    )
    photos = db.relationship(
        "MemberPhoto", back_populates="member", cascade="all, delete-orphan"
    )
    documents = db.relationship(
        "MemberDocument", back_populates="member", cascade="all, delete-orphan"
    )
    trainings = db.relationship(
        "MemberTraining", back_populates="member", cascade="all, delete-orphan"
    )

    @property
    def age(self):
        return _calc_age(self.dob)

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)

    def __repr__(self):
        return f"<Member {self.member_number} {self.full_name}>"


class Spouse(TimestampMixin, db.Model):
    __tablename__ = "spouses"

    id = db.Column("SpouseID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    first_name = db.Column("FirstName", db.String(80))
    last_name = db.Column("LastName", db.String(80))
    dob = db.Column("DOB", db.Date)
    gender = db.Column("Gender", db.String(20))
    email = db.Column("Email", db.String(120))
    phone = db.Column("Phone", db.String(40))
    occupation = db.Column("Occupation", db.String(120))
    photo_path = db.Column("PhotoPath", db.String(255))

    member = db.relationship("Member", back_populates="spouse")

    @property
    def age(self):
        return _calc_age(self.dob)


class Child(TimestampMixin, db.Model):
    __tablename__ = "children"

    id = db.Column("ChildID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    first_name = db.Column("FirstName", db.String(80), nullable=False)
    last_name = db.Column("LastName", db.String(80))
    dob = db.Column("DOB", db.Date)
    gender = db.Column("Gender", db.String(20))
    school = db.Column("School", db.String(120))
    school_class = db.Column("SchoolClass", db.String(80))
    baptism_status = db.Column("BaptismStatus", db.String(40))
    membership_status = db.Column("MembershipStatus", db.String(40))
    photo_path = db.Column("PhotoPath", db.String(255))

    member = db.relationship("Member", back_populates="children")

    @property
    def age(self):
        return _calc_age(self.dob)

    @property
    def full_name(self):
        return " ".join(p for p in [self.first_name, self.last_name] if p)


class MemberPhoto(TimestampMixin, db.Model):
    __tablename__ = "member_photos"

    id = db.Column("PhotoID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    photo_type = db.Column("PhotoType", db.String(40))  # individual/family/spouse
    file_path = db.Column("FilePath", db.String(255), nullable=False)

    member = db.relationship("Member", back_populates="photos")


class MemberDocument(TimestampMixin, db.Model):
    __tablename__ = "member_documents"

    id = db.Column("DocumentID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    document_type = db.Column("DocumentType", db.String(80))
    file_name = db.Column("FileName", db.String(255))
    file_path = db.Column("FilePath", db.String(255), nullable=False)

    member = db.relationship("Member", back_populates="documents")
