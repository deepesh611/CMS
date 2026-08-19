from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Optional

GENDER_CHOICES = [("", "—"), ("Male", "Male"), ("Female", "Female")]
MARITAL_CHOICES = [
    ("", "—"),
    ("Single", "Single"),
    ("Married", "Married"),
    ("Divorced", "Divorced"),
    ("Widowed", "Widowed"),
]
PROFESSIONAL_CATEGORIES = [
    ("", "—"),
    ("Doctor", "Doctor"),
    ("Engineer", "Engineer"),
    ("Pastor", "Pastor"),
    ("Teacher", "Teacher"),
    ("Professor", "Professor"),
    ("Technician", "Technician"),
    ("Nurse", "Nurse"),
    ("Accountant", "Accountant"),
    ("Lawyer", "Lawyer"),
    ("Business Owner", "Business Owner"),
    ("Student", "Student"),
    ("Retired", "Retired"),
    ("Other", "Other"),
]
MEMBERSHIP_STATUS = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
    ("Transferred", "Transferred"),
    ("Deceased", "Deceased"),
]


class MemberForm(FlaskForm):
    # Personal
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=80)])
    middle_name = StringField("Middle Name", validators=[Optional(), Length(max=80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=80)])
    dob = DateField("Date of Birth", validators=[Optional()])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[Optional()])
    nationality = StringField("Nationality", validators=[Optional(), Length(max=80)])
    marital_status = SelectField(
        "Marital Status", choices=MARITAL_CHOICES, validators=[Optional()]
    )

    # Contact
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    personal_email = StringField(
        "Personal Email", validators=[Optional(), Email(), Length(max=120)]
    )
    gsm_number = StringField("GSM Number", validators=[Optional(), Length(max=40)])
    whatsapp_number = StringField(
        "WhatsApp Number", validators=[Optional(), Length(max=40)]
    )
    address = TextAreaField("Residential Address", validators=[Optional()])

    # Employment
    employed = BooleanField("Employed")
    occupation = StringField("Occupation", validators=[Optional(), Length(max=120)])
    employer_name = StringField("Employer Name", validators=[Optional(), Length(max=120)])
    place_of_work = StringField("Place of Work", validators=[Optional(), Length(max=120)])
    professional_category = SelectField(
        "Professional Category", choices=PROFESSIONAL_CATEGORIES, validators=[Optional()]
    )

    # Church
    baptism_date = DateField("Baptism Date", validators=[Optional()])
    joining_date = DateField("Church Joining Date", validators=[Optional()])
    membership_status = SelectField(
        "Membership Status", choices=MEMBERSHIP_STATUS, validators=[Optional()]
    )
    new_member_status = BooleanField("New Member")
    welfare_required = BooleanField("Welfare Support Required")
    care_cell_id = SelectField("Care Cell", coerce=int, validators=[Optional()])

    # Previous church
    mother_church_name = StringField(
        "Mother Church Name", validators=[Optional(), Length(max=120)]
    )
    mother_church_address = StringField(
        "Mother Church Address", validators=[Optional(), Length(max=255)]
    )
    mother_church_country = StringField(
        "Country", validators=[Optional(), Length(max=80)]
    )

    photo = FileField(
        "Photo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only.")],
    )

    submit = SubmitField("Save Member")


class ChildForm(FlaskForm):
    class Meta:
        csrf = False

    first_name = StringField("First Name", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=80)])
    dob = DateField("Date of Birth", validators=[Optional()])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[Optional()])
    school = StringField("School", validators=[Optional(), Length(max=120)])
    school_class = StringField("Class", validators=[Optional(), Length(max=80)])
    baptism_status = StringField("Baptism Status", validators=[Optional(), Length(max=40)])
    membership_status = StringField(
        "Membership Status", validators=[Optional(), Length(max=40)]
    )


class SpouseForm(FlaskForm):
    first_name = StringField("First Name", validators=[Optional(), Length(max=80)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=80)])
    dob = DateField("Date of Birth", validators=[Optional()])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[Optional()])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    occupation = StringField("Occupation", validators=[Optional(), Length(max=120)])
    photo = FileField(
        "Spouse Photo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only.")],
    )
    submit = SubmitField("Save Spouse")


class DocumentForm(FlaskForm):
    document_type = SelectField(
        "Document Type",
        choices=[
            ("Baptism Certificate", "Baptism Certificate"),
            ("Membership Certificate", "Membership Certificate"),
            ("Recommendation Letter", "Recommendation Letter"),
            ("Identification", "Identification Document"),
            ("Award", "Award / Recognition"),
            ("Training Certificate", "Training Certificate"),
            ("Other", "Other"),
        ],
    )
    document = FileField(
        "File",
        validators=[
            DataRequired(),
            FileAllowed(["pdf", "jpg", "jpeg", "png", "docx"], "PDF/JPG/PNG/DOCX only."),
        ],
    )
    submit = SubmitField("Upload")


class TrainingForm(FlaskForm):
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    completion_status = SelectField(
        "Status",
        choices=[
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
            ("Not Started", "Not Started"),
        ],
    )
    completion_date = DateField("Completion Date", validators=[Optional()])
    certificate_number = StringField(
        "Certificate Number", validators=[Optional(), Length(max=80)]
    )
    submit = SubmitField("Add Training")
