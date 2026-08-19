from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.member import ChildForm, SpouseForm
from app.models.member import Child, Member, Spouse
from app.utils.decorators import require_permission
from app.utils.file_upload import save_photo

family_bp = Blueprint("family", __name__, url_prefix="/family")


@family_bp.route("/<int:member_id>/spouse", methods=["GET", "POST"])
@login_required
@require_permission("family", "edit")
def edit_spouse(member_id):
    member = db.get_or_404(Member, member_id)
    spouse = member.spouse or Spouse(member_id=member.id)
    form = SpouseForm(obj=spouse)
    if form.validate_on_submit():
        for field in form:
            if field.name in {"photo", "submit", "csrf_token"}:
                continue
            setattr(spouse, field.name, field.data)
        if form.photo.data and form.photo.data.filename:
            try:
                spouse.photo_path = save_photo(form.photo.data, folder="photos")
            except ValueError as exc:
                flash(str(exc), "error")
        if spouse.id is None:
            db.session.add(spouse)
        db.session.commit()
        flash("Spouse details saved.", "success")
        return redirect(url_for("members.member_detail", member_id=member.id))
    return render_template("family/spouse_form.html", form=form, member=member)


@family_bp.route("/<int:member_id>/children/add", methods=["POST"])
@login_required
@require_permission("family", "edit")
def add_child(member_id):
    member = db.get_or_404(Member, member_id)
    form = ChildForm()
    if form.validate_on_submit():
        child = Child(member_id=member.id)
        for field in form:
            if field.name in {"submit", "csrf_token"}:
                continue
            setattr(child, field.name, field.data)
        db.session.add(child)
        db.session.commit()
        flash("Child added.", "success")
    else:
        flash("Could not add child — check required fields.", "error")
    return redirect(url_for("members.member_detail", member_id=member.id))


@family_bp.route("/children/<int:child_id>/photo", methods=["POST"])
@login_required
@require_permission("family", "edit")
def child_photo(child_id):
    child = db.get_or_404(Child, child_id)
    file = request.files.get("photo")
    if file and file.filename:
        try:
            child.photo_path = save_photo(file, folder="photos")
            db.session.commit()
            flash("Child photo updated.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
    return redirect(url_for("members.member_detail", member_id=child.member_id))


@family_bp.route("/children/<int:child_id>/delete", methods=["POST"])
@login_required
@require_permission("family", "delete")
def delete_child(child_id):
    child = db.get_or_404(Child, child_id)
    member_id = child.member_id
    db.session.delete(child)
    db.session.commit()
    flash("Child removed.", "warning")
    return redirect(url_for("members.member_detail", member_id=member_id))
