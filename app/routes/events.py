from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.events import AssignmentForm, EventForm, SermonForm
from app.models.events import Event, EventAssignment, Pastor, Sermon
from app.models.member import Member
from app.utils.decorators import require_permission

events_bp = Blueprint("events", __name__, url_prefix="/events")


def _member_choices():
    return [
        (m.id, f"{m.full_name} ({m.member_number})")
        for m in Member.query.order_by(Member.last_name)
    ]


def _pastor_choices():
    choices = [(0, "—")]
    for p in Pastor.query.all():
        label = p.member.full_name if p.member else p.position or f"Pastor #{p.id}"
        choices.append((p.id, label))
    return choices


@events_bp.route("/")
@login_required
@require_permission("events", "view")
def list_events():
    items = Event.query.order_by(Event.event_date.desc()).all()
    return render_template("events/list.html", events=items)


@events_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_permission("events", "edit")
def event_create():
    form = EventForm()
    if form.validate_on_submit():
        e = Event(
            name=form.name.data,
            event_type=form.event_type.data,
            event_date=form.event_date.data,
            location=form.location.data,
            notes=form.notes.data,
        )
        db.session.add(e)
        db.session.commit()
        flash("Event created.", "success")
        return redirect(url_for("events.event_detail", event_id=e.id))
    return render_template("events/form.html", form=form, is_new=True)


@events_bp.route("/<int:event_id>", methods=["GET", "POST"])
@login_required
@require_permission("events", "view")
def event_detail(event_id):
    event = db.get_or_404(Event, event_id)
    assign_form = AssignmentForm()
    assign_form.member_id.choices = _member_choices()
    if assign_form.validate_on_submit():
        db.session.add(
            EventAssignment(
                event_id=event.id,
                member_id=assign_form.member_id.data,
                assigned_role=assign_form.assigned_role.data,
            )
        )
        db.session.commit()
        flash("Assignment added.", "success")
        return redirect(url_for("events.event_detail", event_id=event.id))
    return render_template("events/detail.html", event=event, assign_form=assign_form)


@events_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("events", "edit")
def event_edit(event_id):
    event = db.get_or_404(Event, event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("events.event_detail", event_id=event.id))
    return render_template("events/form.html", form=form, is_new=False)


@events_bp.route("/assignments/<int:assignment_id>/remove", methods=["POST"])
@login_required
@require_permission("events", "edit")
def assignment_remove(assignment_id):
    a = db.get_or_404(EventAssignment, assignment_id)
    event_id = a.event_id
    db.session.delete(a)
    db.session.commit()
    flash("Assignment removed.", "warning")
    return redirect(url_for("events.event_detail", event_id=event_id))


# ----------------------------------------------------------------- Sermons
@events_bp.route("/sermons")
@login_required
@require_permission("events", "view")
def sermons():
    items = Sermon.query.order_by(Sermon.service_date.desc()).all()
    return render_template("events/sermons.html", sermons=items)


@events_bp.route("/sermons/new", methods=["GET", "POST"])
@login_required
@require_permission("events", "edit")
def sermon_create():
    form = SermonForm()
    form.pastor_id.choices = _pastor_choices()
    if form.validate_on_submit():
        s = Sermon(
            title=form.title.data,
            scripture_reference=form.scripture_reference.data,
            pastor_id=form.pastor_id.data or None,
            service_date=form.service_date.data,
            service_type=form.service_type.data,
            notes=form.notes.data,
        )
        db.session.add(s)
        db.session.commit()
        flash("Sermon scheduled.", "success")
        return redirect(url_for("events.sermons"))
    return render_template("events/sermon_form.html", form=form)
