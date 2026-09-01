"""Previous church experience routes."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.previous_church import PreviousChurchForm
from app.models.member import Member
from app.models.previous_church import PreviousChurchExperience
from app.utils.decorators import require_permission

previous_church_bp = Blueprint(
    "previous_church", __name__, url_prefix="/previous-church"
)


@previous_church_bp.route("/member/<int:member_id>")
@login_required
@require_permission("members", "view")
def list_experiences(member_id):
    """List all previous church experiences for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    experiences = (
        PreviousChurchExperience.query.filter_by(member_id=member_id)
        .order_by(PreviousChurchExperience.service_start_date.desc())
        .all()
    )
    return render_template(
        "previous_church/list.html",
        member=member,
        experiences=experiences,
    )


@previous_church_bp.route("/member/<int:member_id>/add", methods=["GET", "POST"])
@login_required
@require_permission("members", "edit")
def add_experience(member_id):
    """Add a new previous church experience."""
    member = db.session.get(Member, member_id) or abort(404)
    form = PreviousChurchForm()
    if form.validate_on_submit():
        exp = PreviousChurchExperience(member_id=member_id)
        form.populate_obj(exp)
        db.session.add(exp)
        db.session.commit()
        flash("Previous church experience added.", "success")
        return redirect(
            url_for("previous_church.list_experiences", member_id=member_id)
        )
    return render_template(
        "previous_church/form.html",
        form=form,
        member=member,
        editing=False,
    )


@previous_church_bp.route("/edit/<int:exp_id>", methods=["GET", "POST"])
@login_required
@require_permission("members", "edit")
def edit_experience(exp_id):
    """Edit an existing previous church experience."""
    exp = db.session.get(PreviousChurchExperience, exp_id) or abort(404)
    member = exp.member
    form = PreviousChurchForm(obj=exp)
    if form.validate_on_submit():
        form.populate_obj(exp)
        db.session.commit()
        flash("Previous church experience updated.", "success")
        return redirect(
            url_for("previous_church.list_experiences", member_id=member.id)
        )
    return render_template(
        "previous_church/form.html",
        form=form,
        member=member,
        editing=True,
    )


@previous_church_bp.route("/delete/<int:exp_id>", methods=["POST"])
@login_required
@require_permission("members", "edit")
def delete_experience(exp_id):
    """Delete a previous church experience."""
    exp = db.session.get(PreviousChurchExperience, exp_id) or abort(404)
    member_id = exp.member_id
    db.session.delete(exp)
    db.session.commit()
    flash("Previous church experience deleted.", "warning")
    return redirect(
        url_for("previous_church.list_experiences", member_id=member_id)
    )
