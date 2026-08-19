"""Friday School: classes, students, attendance, activities, performance."""
from app.extensions import db
from app.models.base import TimestampMixin


class FridaySchoolClass(TimestampMixin, db.Model):
    __tablename__ = "friday_school_classes"

    id = db.Column("ClassID", db.Integer, primary_key=True)
    name = db.Column("ClassName", db.String(120), nullable=False)
    teacher_id = db.Column("TeacherID", db.Integer, db.ForeignKey("members.MemberID"))
    assistant_teacher_id = db.Column(
        "AssistantTeacherID", db.Integer, db.ForeignKey("members.MemberID")
    )
    age_group = db.Column("AgeGroup", db.String(80))

    teacher = db.relationship("Member", foreign_keys=[teacher_id])
    assistant_teacher = db.relationship("Member", foreign_keys=[assistant_teacher_id])
    students = db.relationship(
        "FridaySchoolStudent", back_populates="fs_class", cascade="all, delete-orphan"
    )
    activities = db.relationship(
        "FridaySchoolActivity", back_populates="fs_class", cascade="all, delete-orphan"
    )


class FridaySchoolStudent(TimestampMixin, db.Model):
    __tablename__ = "friday_school_students"

    id = db.Column("StudentID", db.Integer, primary_key=True)
    child_id = db.Column("ChildID", db.Integer, db.ForeignKey("children.ChildID"))
    class_id = db.Column(
        "ClassID", db.Integer, db.ForeignKey("friday_school_classes.ClassID")
    )

    child = db.relationship("Child")
    fs_class = db.relationship("FridaySchoolClass", back_populates="students")
    attendance = db.relationship(
        "FridaySchoolAttendance", back_populates="student", cascade="all, delete-orphan"
    )
    performance = db.relationship(
        "FridaySchoolPerformance", back_populates="student", cascade="all, delete-orphan"
    )


class FridaySchoolAttendance(TimestampMixin, db.Model):
    __tablename__ = "friday_school_attendance"

    id = db.Column("AttendanceID", db.Integer, primary_key=True)
    student_id = db.Column(
        "StudentID",
        db.Integer,
        db.ForeignKey("friday_school_students.StudentID"),
        nullable=False,
    )
    attendance_date = db.Column("AttendanceDate", db.Date, index=True)
    status = db.Column("Status", db.String(20), default="Present")

    student = db.relationship("FridaySchoolStudent", back_populates="attendance")


class FridaySchoolActivity(TimestampMixin, db.Model):
    __tablename__ = "friday_school_activities"

    id = db.Column("ActivityID", db.Integer, primary_key=True)
    class_id = db.Column(
        "ClassID", db.Integer, db.ForeignKey("friday_school_classes.ClassID")
    )
    name = db.Column("ActivityName", db.String(150), nullable=False)
    activity_date = db.Column("ActivityDate", db.Date)
    teacher_notes = db.Column("TeacherNotes", db.Text)

    fs_class = db.relationship("FridaySchoolClass", back_populates="activities")


class FridaySchoolPerformance(TimestampMixin, db.Model):
    __tablename__ = "friday_school_performance"

    id = db.Column("PerformanceID", db.Integer, primary_key=True)
    student_id = db.Column(
        "StudentID",
        db.Integer,
        db.ForeignKey("friday_school_students.StudentID"),
        nullable=False,
    )
    assessment = db.Column("Assessment", db.String(120))
    behavior = db.Column("Behavior", db.String(120))
    participation = db.Column("Participation", db.String(120))
    achievements = db.Column("Achievements", db.Text)
    remarks = db.Column("Remarks", db.Text)

    student = db.relationship("FridaySchoolStudent", back_populates="performance")
