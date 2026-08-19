"""Discipleship / leadership / ministry training courses."""
from app.extensions import db
from app.models.base import TimestampMixin


class TrainingCourse(TimestampMixin, db.Model):
    __tablename__ = "training_courses"

    id = db.Column("CourseID", db.Integer, primary_key=True)
    name = db.Column("CourseName", db.String(120), nullable=False)
    level = db.Column("CourseLevel", db.String(80))
    is_mandatory_for_leadership = db.Column(
        "MandatoryForLeadership", db.Boolean, default=False
    )

    member_trainings = db.relationship(
        "MemberTraining", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TrainingCourse {self.name}>"


class MemberTraining(TimestampMixin, db.Model):
    __tablename__ = "member_training"

    id = db.Column("MemberTrainingID", db.Integer, primary_key=True)
    member_id = db.Column(
        "MemberID", db.Integer, db.ForeignKey("members.MemberID"), nullable=False
    )
    course_id = db.Column(
        "CourseID", db.Integer, db.ForeignKey("training_courses.CourseID"), nullable=False
    )
    completion_status = db.Column("CompletionStatus", db.String(40), default="In Progress")
    completion_date = db.Column("CompletionDate", db.Date)
    certificate_number = db.Column("CertificateNumber", db.String(80))

    member = db.relationship("Member", back_populates="trainings")
    course = db.relationship("TrainingCourse", back_populates="member_trainings")
