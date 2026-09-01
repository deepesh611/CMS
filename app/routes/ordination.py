"""Ordination management routes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.ordination import OrdinationForm
from app.models.member import Member
from app.models.ordination import Ordination
from app.utils.decorators import require_permission
from app.utils.file_upload import save_document

ordination_bp = Blueprint("ordination", __name__, url_prefix="/ordination")


@ordination_bp.route("/")
@login_required
@require_permission("ordination", "view")
def list_ordained():
    """List all ordained ministers."""
    ordained = (
        Ordination.query.filter_by(is_ordained=True)
        .order_by(Ordination.ordination_date.desc())
        .all()
    )
    return render_template("ordination/list.html", ordained=ordained)


@ordination_bp.route("/directory")
@login_required
@require_permission("ordination", "view")
def directory():
    """Ordained ministers directory."""
    ordained = (
        Ordination.query.filter_by(is_ordained=True)
        .order_by(Ordination.ordination_date)
        .all()
    )
    return render_template("ordination/directory.html", ordained=ordained)


@ordination_bp.route("/member/<int:member_id>")
@login_required
@require_permission("ordination", "view")
def detail(member_id):
    """View ordination detail for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    return render_template("ordination/detail.html", member=member)


@ordination_bp.route("/member/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("ordination", "edit")
def edit(member_id):
    """Create or update ordination record for a member."""
    member = db.session.get(Member, member_id) or abort(404)
    ordination = member.ordination or Ordination(member_id=member_id)

    form = OrdinationForm(obj=ordination)
    if form.validate_on_submit():
        form.populate_obj(ordination)

        # Handle certificate upload
        cert_file = request.files.get("certificate_file")
        if cert_file and cert_file.filename:
            path = save_document(cert_file, member_id)
            ordination.certificate_path = path

        if not ordination.id:
            db.session.add(ordination)
        db.session.commit()
        flash("Ordination record updated.", "success")
        return redirect(url_for("ordination.detail", member_id=member_id))

    return render_template(
        "ordination/form.html",
        form=form,
        member=member,
    )
