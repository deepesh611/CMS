from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.outreach import FollowupForm, OutreachProgramForm, VisitorForm
from app.models.outreach import (
    OutreachProgram,
    Visitor,
    VisitorFollowup,
)
from app.utils.decorators import require_permission

outreach_bp = Blueprint("outreach", __name__, url_prefix="/outreach")


# ------------------------------------------------------------- Outreach programs
@outreach_bp.route("/programs")
@login_required
@require_permission("outreach", "view")
def programs():
    items = OutreachProgram.query.order_by(OutreachProgram.outreach_date.desc()).all()
    return render_template("outreach/programs.html", programs=items)


@outreach_bp.route("/programs/new", methods=["GET", "POST"])
@login_required
@require_permission("outreach", "edit")
def program_create():
    form = OutreachProgramForm()
    if form.validate_on_submit():
        p = OutreachProgram(
            name=form.name.data,
            outreach_date=form.outreach_date.data,
            location=form.location.data,
            organizers=form.organizers.data,
            team_members=form.team_members.data,
        )
        db.session.add(p)
        db.session.commit()
        flash("Outreach program created.", "success")
        return redirect(url_for("outreach.programs"))
    return render_template("outreach/program_form.html", form=form, is_new=True)


@outreach_bp.route("/programs/<int:program_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("outreach", "edit")
def program_edit(program_id):
    p = db.get_or_404(OutreachProgram, program_id)
    form = OutreachProgramForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data
        p.outreach_date = form.outreach_date.data
        p.location = form.location.data
        p.organizers = form.organizers.data
        p.team_members = form.team_members.data
        db.session.commit()
        flash("Outreach program updated.", "success")
        return redirect(url_for("outreach.programs"))
    return render_template("outreach/program_form.html", form=form, is_new=False)


# --------------------------------------------------------------------- Visitors
@outreach_bp.route("/visitors")
@login_required
@require_permission("visitors", "view")
def visitors():
    items = Visitor.query.order_by(Visitor.visit_date.desc()).all()
    return render_template("outreach/visitors.html", visitors=items)


@outreach_bp.route("/visitors/new", methods=["GET", "POST"])
@login_required
@require_permission("visitors", "edit")
def visitor_create():
    form = VisitorForm()
    if form.validate_on_submit():
        v = Visitor()
        _apply(form, v)
        db.session.add(v)
        db.session.commit()
        flash("Visitor recorded.", "success")
        return redirect(url_for("outreach.visitor_detail", visitor_id=v.id))
    return render_template("outreach/visitor_form.html", form=form, is_new=True)


@outreach_bp.route("/visitors/<int:visitor_id>", methods=["GET", "POST"])
@login_required
@require_permission("visitors", "view")
def visitor_detail(visitor_id):
    visitor = db.get_or_404(Visitor, visitor_id)
    form = FollowupForm()
    if form.validate_on_submit():
        db.session.add(
            VisitorFollowup(
                visitor_id=visitor.id,
                followup_date=form.followup_date.data,
                assigned_worker=form.assigned_worker.data,
                outcome=form.outcome.data,
            )
        )
        db.session.commit()
        flash("Follow-up recorded.", "success")
        return redirect(url_for("outreach.visitor_detail", visitor_id=visitor.id))
    return render_template("outreach/visitor_detail.html", visitor=visitor, form=form)


@outreach_bp.route("/visitors/<int:visitor_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("visitors", "edit")
def visitor_edit(visitor_id):
    visitor = db.get_or_404(Visitor, visitor_id)
    form = VisitorForm(obj=visitor)
    if form.validate_on_submit():
        _apply(form, visitor)
        db.session.commit()
        flash("Visitor updated.", "success")
        return redirect(url_for("outreach.visitor_detail", visitor_id=visitor.id))
    return render_template("outreach/visitor_form.html", form=form, is_new=False)


def _apply(form, visitor):
    for field in form:
        if field.name in {"submit", "csrf_token"}:
            continue
        setattr(visitor, field.name, field.data)
