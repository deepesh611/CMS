"""Discipleship tracking and ministry eligibility routes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.discipleship import DiscipleshipProgressForm, EligibilityOverrideForm
from app.models.discipleship import DiscipleshipProgress, EligibilityOverride
from app.models.member import Member
from app.utils.decorators import require_permission

discipleship_bp = Blueprint("discipleship", __name__, url_prefix="/discipleship")


@discipleship_bp.route("/")
@login_required
@require_permission("discipleship", "view")
def dashboard():
    """Discipleship overview dashboard."""
    members = Member.query.order_by(Member.first_name).all()

    # Statistics
    total = len(members)
    with_progress = [m for m in members if m.discipleship_progress]
    fully_eligible = [m for m in members if m.is_ministry_eligible]
    in_progress = [
        m
        for m in with_progress
        if not m.discipleship_progress.is_all_completed
    ]
    not_started = total - len(with_progress)

    # Per-level completion counts
    level_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for m in with_progress:
        dp = m.discipleship_progress
        if dp.level1_status == "Completed":
            level_counts[1] += 1
        if dp.level2_status == "Completed":
            level_counts[2] += 1
        if dp.level3_status == "Completed":
            level_counts[3] += 1
        if dp.level4_status == "Completed":
            level_counts[4] += 1

    return render_template(
        "discipleship/dashboard.html",
        members=members,
        total=total,
        fully_eligible=len(fully_eligible),
        in_progress=len(in_progress),
        not_started=not_started,
        level_counts=level_counts,
    )


@discipleship_bp.route("/member/<int:member_id>")
@login_required
@require_permission("discipleship", "view")
def member_progress(member_id):
    """View a member's discipleship progress detail."""
    member = db.session.get(Member, member_id) or abort(404)
    overrides = EligibilityOverride.query.filter_by(member_id=member_id).order_by(
        EligibilityOverride.override_date.desc()
    ).all()
    return render_template(
        "discipleship/member_progress.html",
        member=member,
        overrides=overrides,
    )


@discipleship_bp.route("/member/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("discipleship", "edit")
def edit_progress(member_id):
    """Create or update discipleship progress for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    progress = member.discipleship_progress or DiscipleshipProgress(member_id=member_id)

    form = DiscipleshipProgressForm(obj=progress)
    if form.validate_on_submit():
        form.populate_obj(progress)
        if not progress.id:
            db.session.add(progress)
        db.session.commit()
        flash("Discipleship progress updated.", "success")
        return redirect(url_for("discipleship.member_progress", member_id=member_id))

    return render_template(
        "discipleship/edit_progress.html",
        form=form,
        member=member,
    )


@discipleship_bp.route("/member/<int:member_id>/override", methods=["GET", "POST"])
@login_required
@require_permission("discipleship", "edit")
def create_override(member_id):
    """Create an eligibility override for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    form = EligibilityOverrideForm()
    if form.validate_on_submit():
        override = EligibilityOverride(
            member_id=member_id,
            override_reason=form.override_reason.data,
            approved_by_user_id=current_user.id,
        )
        db.session.add(override)
        db.session.commit()
        flash("Eligibility override created and recorded in audit trail.", "success")
        return redirect(url_for("discipleship.member_progress", member_id=member_id))

    return render_template(
        "discipleship/override_form.html",
        form=form,
        member=member,
    )
