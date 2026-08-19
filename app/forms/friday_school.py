from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class FSClassForm(FlaskForm):
    name = StringField("Class Name", validators=[DataRequired(), Length(max=120)])
    teacher_id = SelectField("Teacher", coerce=int, validators=[Optional()])
    assistant_teacher_id = SelectField(
        "Assistant Teacher", coerce=int, validators=[Optional()]
    )
    age_group = StringField("Age Group", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Save")


class FSStudentForm(FlaskForm):
    child_id = SelectField("Child", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Enroll Student")


class FSActivityForm(FlaskForm):
    name = StringField("Activity Name", validators=[DataRequired(), Length(max=150)])
    activity_date = DateField("Date", validators=[Optional()])
    teacher_notes = TextAreaField("Teacher Notes", validators=[Optional()])
    submit = SubmitField("Add Activity")


class FSPerformanceForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, validators=[DataRequired()])
    assessment = StringField("Assessment", validators=[Optional(), Length(max=120)])
    behavior = StringField("Behavior", validators=[Optional(), Length(max=120)])
    participation = StringField("Participation", validators=[Optional(), Length(max=120)])
    achievements = TextAreaField("Achievements", validators=[Optional()])
    remarks = TextAreaField("Remarks", validators=[Optional()])
    submit = SubmitField("Save Performance")
