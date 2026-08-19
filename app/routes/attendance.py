from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.models.events import Attendance, Event
from app.models.member import Member
from app.utils.decorators import require_permission

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance_bp.route("/")
@login_required
@require_permission("attendance", "view")
def index():
    events = Event.query.order_by(Event.event_date.desc()).limit(50).all()
    return render_template("attendance/index.html", events=events)


@attendance_bp.route("/event/<int:event_id>", methods=["GET", "POST"])
@login_required
@require_permission("attendance", "edit")
def mark(event_id):
    event = db.get_or_404(Event, event_id)
    members = Member.query.order_by(Member.last_name, Member.first_name).all()

    if request.method == "POST":
        present_ids = set(request.form.getlist("present", type=int))
        att_date = event.event_date or date.today()

        # Clear prior attendance for this event, then re-record
        Attendance.query.filter_by(event_id=event.id).delete()
        for m in members:
            db.session.add(
                Attendance(
                    member_id=m.id,
                    event_id=event.id,
                    attendance_date=att_date,
                    status="Present" if m.id in present_ids else "Absent",
                )
            )
        db.session.commit()
        flash(f"Attendance saved: {len(present_ids)} present.", "success")
        return redirect(url_for("attendance.mark", event_id=event.id))

    existing = {
        a.member_id: a.status
        for a in Attendance.query.filter_by(event_id=event.id).all()
    }
    return render_template(
        "attendance/mark.html", event=event, members=members, existing=existing
    )


@attendance_bp.route("/report")
@login_required
@require_permission("attendance", "view")
def report():
    from sqlalchemy import func

    rows = (
        db.session.query(
            Event.name,
            Event.event_date,
            func.sum(db.case((Attendance.status == "Present", 1), else_=0)).label(
                "present"
            ),
            func.count(Attendance.id).label("total"),
        )
        .join(Attendance, Attendance.event_id == Event.id)
        .group_by(Event.id)
        .order_by(Event.event_date.desc())
        .all()
    )
    return render_template("attendance/report.html", rows=rows)
