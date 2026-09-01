"""Member exit, relocation, and church transfer routes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.member_exit import MemberExitForm
from app.models.member import Member
from app.models.member_exit import MemberExit
from app.utils.decorators import require_permission

member_exit_bp = Blueprint("member_exit", __name__, url_prefix="/exit")


@member_exit_bp.route("/")
@login_required
@require_permission("member_exit", "view")
def list_exits():
    """List all former / departed members."""
    q = request.args.get("q", "").strip()
    query = MemberExit.query.join(Member)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Member.first_name.ilike(like),
                Member.last_name.ilike(like),
                MemberExit.exit_category.ilike(like),
                MemberExit.dest_country.ilike(like),
            )
        )
    exits = query.order_by(MemberExit.exit_date.desc()).all()
    return render_template("member_exit/list.html", exits=exits, q=q)


@member_exit_bp.route("/new/<int:member_id>", methods=["GET", "POST"])
@login_required
@require_permission("member_exit", "edit")
def create_exit(member_id):
    """Process a member's departure."""
    member = db.session.get(Member, member_id) or abort(404)

    # Prevent duplicate exit records
    if member.exit_record:
        flash("This member already has an exit record.", "warning")
        return redirect(url_for("member_exit.detail", exit_id=member.exit_record.id))

    form = MemberExitForm()
    if form.validate_on_submit():
        exit_record = MemberExit(member_id=member_id)
        form.populate_obj(exit_record)
        db.session.add(exit_record)

        # Update member status to Former
        member.membership_status = "Former"
        db.session.commit()
        flash(
            f"{member.full_name} has been processed as a former member.",
            "success",
        )
        return redirect(url_for("member_exit.detail", exit_id=exit_record.id))

    return render_template(
        "member_exit/form.html",
        form=form,
        member=member,
    )


@member_exit_bp.route("/detail/<int:exit_id>")
@login_required
@require_permission("member_exit", "view")
def detail(exit_id):
    """View complete exit record."""
    exit_record = db.session.get(MemberExit, exit_id) or abort(404)
    return render_template("member_exit/detail.html", exit_record=exit_record)


@member_exit_bp.route("/edit/<int:exit_id>", methods=["GET", "POST"])
@login_required
@require_permission("member_exit", "edit")
def edit_exit(exit_id):
    """Edit an existing exit record."""
    exit_record = db.session.get(MemberExit, exit_id) or abort(404)
    member = exit_record.member
    form = MemberExitForm(obj=exit_record)
    if form.validate_on_submit():
        form.populate_obj(exit_record)
        db.session.commit()
        flash("Exit record updated.", "success")
        return redirect(url_for("member_exit.detail", exit_id=exit_id))

    return render_template(
        "member_exit/form.html",
        form=form,
        member=member,
        editing=True,
    )
