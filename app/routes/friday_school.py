from datetime import date

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.friday_school import (
    FSActivityForm,
    FSClassForm,
    FSPerformanceForm,
    FSStudentForm,
)
from app.models.friday_school import (
    FridaySchoolActivity,
    FridaySchoolAttendance,
    FridaySchoolClass,
    FridaySchoolPerformance,
    FridaySchoolStudent,
)
from app.models.member import Child, Member
from app.utils.decorators import require_permission

friday_school_bp = Blueprint("friday_school", __name__, url_prefix="/friday-school")


def _member_choices():
    return [(0, "—")] + [
        (m.id, m.full_name) for m in Member.query.order_by(Member.last_name)
    ]


def _can_manage_class(fs_class):
    """Coordinators/admins manage any class; teachers only their own."""
    role = current_user.role.name if current_user.role else ""
    if role in {"Super Administrator", "IT Administrator", "Friday School Coordinator",
                "Church Administrator"}:
        return True
    if role == "Friday School Teacher" and current_user.member_id:
        return current_user.member_id in {
            fs_class.teacher_id,
            fs_class.assistant_teacher_id,
        }
    return current_user.has_permission("friday_school", "edit")


@friday_school_bp.route("/classes")
@login_required
@require_permission("friday_school", "view")
def classes():
    items = FridaySchoolClass.query.order_by(FridaySchoolClass.name).all()
    return render_template("friday_school/classes.html", classes=items)


@friday_school_bp.route("/classes/new", methods=["GET", "POST"])
@login_required
@require_permission("friday_school", "edit")
def class_create():
    form = FSClassForm()
    form.teacher_id.choices = _member_choices()
    form.assistant_teacher_id.choices = _member_choices()
    if form.validate_on_submit():
        c = FridaySchoolClass(
            name=form.name.data,
            teacher_id=form.teacher_id.data or None,
            assistant_teacher_id=form.assistant_teacher_id.data or None,
            age_group=form.age_group.data,
        )
        db.session.add(c)
        db.session.commit()
        flash("Class created.", "success")
        return redirect(url_for("friday_school.class_detail", class_id=c.id))
    return render_template("friday_school/class_form.html", form=form, is_new=True)


@friday_school_bp.route("/classes/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_permission("friday_school", "view")
def class_detail(class_id):
    fs_class = db.get_or_404(FridaySchoolClass, class_id)
    student_form = FSStudentForm()
    enrolled_ids = {s.child_id for s in fs_class.students}
    student_form.child_id.choices = [
        (c.id, c.full_name)
        for c in Child.query.order_by(Child.first_name)
        if c.id not in enrolled_ids
    ] or [(0, "No unenrolled children")]
    activity_form = FSActivityForm()
    perf_form = FSPerformanceForm()
    perf_form.student_id.choices = [
        (s.id, s.child.full_name if s.child else f"Student #{s.id}")
        for s in fs_class.students
    ] or [(0, "No students")]

    return render_template(
        "friday_school/class_detail.html",
        fs_class=fs_class,
        student_form=student_form,
        activity_form=activity_form,
        perf_form=perf_form,
        can_manage=_can_manage_class(fs_class),
    )


@friday_school_bp.route("/classes/<int:class_id>/students", methods=["POST"])
@login_required
@require_permission("friday_school", "edit")
def add_student(class_id):
    fs_class = db.get_or_404(FridaySchoolClass, class_id)
    if not _can_manage_class(fs_class):
        abort(403)
    child_id = request.form.get("child_id", type=int)
    if child_id:
        db.session.add(
            FridaySchoolStudent(child_id=child_id, class_id=fs_class.id)
        )
        db.session.commit()
        flash("Student enrolled.", "success")
    return redirect(url_for("friday_school.class_detail", class_id=fs_class.id))


@friday_school_bp.route("/classes/<int:class_id>/attendance", methods=["GET", "POST"])
@login_required
@require_permission("friday_school", "edit")
def attendance(class_id):
    fs_class = db.get_or_404(FridaySchoolClass, class_id)
    if not _can_manage_class(fs_class):
        abort(403)
    if request.method == "POST":
        att_date = request.form.get("attendance_date") or date.today().isoformat()
        present = set(request.form.getlist("present", type=int))
        for student in fs_class.students:
            db.session.add(
                FridaySchoolAttendance(
                    student_id=student.id,
                    attendance_date=date.fromisoformat(att_date),
                    status="Present" if student.id in present else "Absent",
                )
            )
        db.session.commit()
        flash("Attendance recorded.", "success")
        return redirect(url_for("friday_school.class_detail", class_id=fs_class.id))
    return render_template(
        "friday_school/attendance.html", fs_class=fs_class, today=date.today().isoformat()
    )


@friday_school_bp.route("/classes/<int:class_id>/activities", methods=["POST"])
@login_required
@require_permission("friday_school", "edit")
def add_activity(class_id):
    fs_class = db.get_or_404(FridaySchoolClass, class_id)
    if not _can_manage_class(fs_class):
        abort(403)
    form = FSActivityForm()
    if form.validate_on_submit():
        db.session.add(
            FridaySchoolActivity(
                class_id=fs_class.id,
                name=form.name.data,
                activity_date=form.activity_date.data,
                teacher_notes=form.teacher_notes.data,
            )
        )
        db.session.commit()
        flash("Activity added.", "success")
    return redirect(url_for("friday_school.class_detail", class_id=fs_class.id))


@friday_school_bp.route("/classes/<int:class_id>/performance", methods=["POST"])
@login_required
@require_permission("friday_school", "edit")
def add_performance(class_id):
    fs_class = db.get_or_404(FridaySchoolClass, class_id)
    if not _can_manage_class(fs_class):
        abort(403)
    form = FSPerformanceForm()
    form.student_id.choices = [(s.id, "") for s in fs_class.students]
    if form.validate_on_submit():
        db.session.add(
            FridaySchoolPerformance(
                student_id=form.student_id.data,
                assessment=form.assessment.data,
                behavior=form.behavior.data,
                participation=form.participation.data,
                achievements=form.achievements.data,
                remarks=form.remarks.data,
            )
        )
        db.session.commit()
        flash("Performance recorded.", "success")
    return redirect(url_for("friday_school.class_detail", class_id=fs_class.id))
