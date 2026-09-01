from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm

from app.extensions import db
from app.forms.church import (
    CareCellForm,
    MinistryForm,
    MinistryMemberForm,
)
from app.models.church import (
    CareCell,
    CareCellMember,
    Ministry,
    MinistryMember,
    MinistryMovement,
    MemberLeadership,
    LeadershipRole,
)
from app.models.member import Member
from app.utils.decorators import require_permission


class MinistryMovementForm(FlaskForm):
    """Form for recording a ministry transfer or movement."""

    movement_type = SelectField(
        "Movement Type",
        choices=[(t, t) for t in MinistryMovement.MOVEMENT_TYPES],
        validators=[DataRequired()],
    )
    previous_ministry_id = SelectField(
        "Previous Ministry", coerce=int, validators=[Optional()]
    )
    new_ministry_id = SelectField(
        "New Ministry", coerce=int, validators=[Optional()]
    )
    previous_role = StringField("Previous Role", validators=[Optional()])
    new_role = StringField("New Role", validators=[Optional()])
    effective_date = DateField(
        "Effective Date", validators=[DataRequired()]
    )
    last_date_previous = DateField(
        "Last Date in Previous Ministry", validators=[Optional()]
    )
    reason = TextAreaField("Reason for Change", validators=[Optional()])
    approved_by = StringField("Approved By", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

church_bp = Blueprint("church", __name__, url_prefix="/church")


def _member_choices(optional=True):
    members = Member.query.order_by(Member.last_name, Member.first_name).all()
    choices = [(m.id, f"{m.full_name} ({m.member_number})") for m in members]
    return ([(0, "—")] + choices) if optional else choices


# ------------------------------------------------------------------ Ministries
@church_bp.route("/ministries")
@login_required
@require_permission("ministries", "view")
def ministries():
    items = Ministry.query.order_by(Ministry.name).all()
    return render_template("church/ministries.html", ministries=items)


@church_bp.route("/ministries/new", methods=["GET", "POST"])
@login_required
@require_permission("ministries", "edit")
def ministry_create():
    form = MinistryForm()
    if form.validate_on_submit():
        m = Ministry(name=form.name.data, description=form.description.data)
        db.session.add(m)
        db.session.commit()
        flash("Ministry created.", "success")
        return redirect(url_for("church.ministry_detail", ministry_id=m.id))
    return render_template("church/ministry_form.html", form=form, is_new=True)


@church_bp.route("/ministries/<int:ministry_id>", methods=["GET", "POST"])
@login_required
@require_permission("ministries", "view")
def ministry_detail(ministry_id):
    ministry = db.get_or_404(Ministry, ministry_id)
    form = MinistryMemberForm()
    form.member_id.choices = _member_choices(optional=False)
    if form.validate_on_submit():
        db.session.add(
            MinistryMember(
                ministry_id=ministry.id,
                member_id=form.member_id.data,
                ministry_role=form.ministry_role.data,
            )
        )
        db.session.commit()
        flash("Member added to ministry.", "success")
        return redirect(url_for("church.ministry_detail", ministry_id=ministry.id))
    return render_template("church/ministry_detail.html", ministry=ministry, form=form)


@church_bp.route("/ministries/<int:ministry_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("ministries", "edit")
def ministry_edit(ministry_id):
    ministry = db.get_or_404(Ministry, ministry_id)
    form = MinistryForm(obj=ministry)
    if form.validate_on_submit():
        ministry.name = form.name.data
        ministry.description = form.description.data
        db.session.commit()
        flash("Ministry updated.", "success")
        return redirect(url_for("church.ministry_detail", ministry_id=ministry.id))
    return render_template("church/ministry_form.html", form=form, is_new=False)


@church_bp.route("/ministry-members/<int:mm_id>/remove", methods=["POST"])
@login_required
@require_permission("ministries", "edit")
def ministry_member_remove(mm_id):
    mm = db.get_or_404(MinistryMember, mm_id)
    ministry_id = mm.ministry_id
    db.session.delete(mm)
    db.session.commit()
    flash("Member removed.", "warning")
    return redirect(url_for("church.ministry_detail", ministry_id=ministry_id))


# ------------------------------------------------------------------ Care Cells
@church_bp.route("/care-cells")
@login_required
@require_permission("care_cells", "view")
def care_cells():
    items = CareCell.query.order_by(CareCell.name).all()
    return render_template("church/care_cells.html", care_cells=items)


@church_bp.route("/care-cells/new", methods=["GET", "POST"])
@login_required
@require_permission("care_cells", "edit")
def care_cell_create():
    form = CareCellForm()
    form.leader_id.choices = _member_choices()
    form.assistant_leader_id.choices = _member_choices()
    if form.validate_on_submit():
        cell = CareCell(
            name=form.name.data,
            leader_id=form.leader_id.data or None,
            assistant_leader_id=form.assistant_leader_id.data or None,
            location=form.location.data,
            meeting_schedule=form.meeting_schedule.data,
        )
        db.session.add(cell)
        db.session.commit()
        flash("Care cell created.", "success")
        return redirect(url_for("church.care_cell_detail", cell_id=cell.id))
    return render_template("church/care_cell_form.html", form=form, is_new=True)


@church_bp.route("/care-cells/<int:cell_id>", methods=["GET", "POST"])
@login_required
@require_permission("care_cells", "view")
def care_cell_detail(cell_id):
    cell = db.get_or_404(CareCell, cell_id)
    form = MinistryMemberForm()  # reuse member+role widget (role unused here)
    form.member_id.choices = _member_choices(optional=False)
    if form.validate_on_submit():
        exists = CareCellMember.query.filter_by(
            care_cell_id=cell.id, member_id=form.member_id.data
        ).first()
        if not exists:
            db.session.add(
                CareCellMember(care_cell_id=cell.id, member_id=form.member_id.data)
            )
            db.session.commit()
            flash("Member added to care cell.", "success")
        return redirect(url_for("church.care_cell_detail", cell_id=cell.id))
    return render_template("church/care_cell_detail.html", cell=cell, form=form)


@church_bp.route("/care-cells/<int:cell_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("care_cells", "edit")
def care_cell_edit(cell_id):
    cell = db.get_or_404(CareCell, cell_id)
    form = CareCellForm(obj=cell)
    form.leader_id.choices = _member_choices()
    form.assistant_leader_id.choices = _member_choices()
    if form.validate_on_submit():
        cell.name = form.name.data
        cell.leader_id = form.leader_id.data or None
        cell.assistant_leader_id = form.assistant_leader_id.data or None
        cell.location = form.location.data
        cell.meeting_schedule = form.meeting_schedule.data
        db.session.commit()
        flash("Care cell updated.", "success")
        return redirect(url_for("church.care_cell_detail", cell_id=cell.id))
    return render_template("church/care_cell_form.html", form=form, is_new=False)


@church_bp.route("/carecell-members/<int:cm_id>/remove", methods=["POST"])
@login_required
@require_permission("care_cells", "edit")
def care_cell_member_remove(cm_id):
    cm = db.get_or_404(CareCellMember, cm_id)
    cell_id = cm.care_cell_id
    db.session.delete(cm)
    db.session.commit()
    flash("Member removed.", "warning")
    return redirect(url_for("church.care_cell_detail", cell_id=cell_id))


# ─── Ministry Movement / Transfer ────────────────────────────────────

def _ministry_choices():
    return [(0, "— None —")] + [
        (m.id, m.name) for m in Ministry.query.order_by(Ministry.name).all()
    ]


@church_bp.route("/movements/member/<int:member_id>")
@login_required
@require_permission("ministries", "view")
def member_movements(member_id):
    """View ministry movement history for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    movements = (
        MinistryMovement.query.filter_by(member_id=member_id)
        .order_by(MinistryMovement.effective_date.desc())
        .all()
    )
    return render_template(
        "church/member_movements.html",
        member=member,
        movements=movements,
    )


@church_bp.route("/movements/member/<int:member_id>/add", methods=["GET", "POST"])
@login_required
@require_permission("ministries", "edit")
def add_movement(member_id):
    """Record a ministry transfer / movement for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    form = MinistryMovementForm()
    form.previous_ministry_id.choices = _ministry_choices()
    form.new_ministry_id.choices = _ministry_choices()

    if form.validate_on_submit():
        mov = MinistryMovement(member_id=member_id)
        form.populate_obj(mov)
        if mov.previous_ministry_id == 0:
            mov.previous_ministry_id = None
        if mov.new_ministry_id == 0:
            mov.new_ministry_id = None
        db.session.add(mov)
        db.session.commit()
        flash("Ministry movement recorded.", "success")
        return redirect(
            url_for("church.member_movements", member_id=member_id)
        )
    return render_template(
        "church/movement_form.html",
        form=form,
        member=member,
    )


# ─── Leadership History ──────────────────────────────────────────────

@church_bp.route("/leadership/member/<int:member_id>")
@login_required
@require_permission("ministries", "view")
def leadership_timeline(member_id):
    """View leadership history timeline for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    entries = (
        MemberLeadership.query.filter_by(member_id=member_id)
        .order_by(MemberLeadership.appointment_date.desc())
        .all()
    )
    return render_template(
        "church/leadership_timeline.html",
        member=member,
        entries=entries,
    )
