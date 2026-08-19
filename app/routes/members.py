from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.forms.member import DocumentForm, MemberForm, TrainingForm
from app.models.church import CareCell
from app.models.member import Member, MemberDocument, MemberPhoto
from app.models.training import MemberTraining, TrainingCourse
from app.utils.decorators import require_permission
from app.utils.file_upload import save_document, save_photo
from app.utils.storage import storage

members_bp = Blueprint("members", __name__, url_prefix="/members")


def _next_member_number():
    last = Member.query.order_by(Member.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f"MBR-{n:05d}"


def _populate_choices(form):
    cells = CareCell.query.order_by(CareCell.name).all()
    form.care_cell_id.choices = [(0, "—")] + [(c.id, c.name) for c in cells]


@members_bp.route("/")
@login_required
@require_permission("members", "view")
def list_members():
    q = request.args.get("q", "").strip()
    query = Member.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(like),
                Member.last_name.ilike(like),
                Member.member_number.ilike(like),
                Member.email.ilike(like),
                Member.gsm_number.ilike(like),
            )
        )
    page = request.args.get("page", 1, type=int)
    members = query.order_by(Member.last_name, Member.first_name).paginate(
        page=page, per_page=25, error_out=False
    )
    return render_template("members/list.html", members=members, q=q)


@members_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_permission("members", "edit")
def member_create():
    form = MemberForm()
    _populate_choices(form)
    if form.validate_on_submit():
        member = Member(member_number=_next_member_number())
        _apply_form(form, member)
        db.session.add(member)
        db.session.flush()
        _handle_photo(form, member, "individual")
        db.session.commit()
        flash(f"Member {member.member_number} created.", "success")
        return redirect(url_for("members.member_detail", member_id=member.id))
    return render_template("members/form.html", form=form, is_new=True)


@members_bp.route("/<int:member_id>")
@login_required
@require_permission("members", "view")
def member_detail(member_id):
    member = db.get_or_404(Member, member_id)
    doc_form = DocumentForm()
    training_form = TrainingForm()
    training_form.course_id.choices = [
        (c.id, c.name) for c in TrainingCourse.query.order_by(TrainingCourse.name)
    ]
    return render_template(
        "members/detail.html",
        member=member,
        doc_form=doc_form,
        training_form=training_form,
    )


@members_bp.route("/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("members", "edit")
def member_edit(member_id):
    member = db.get_or_404(Member, member_id)
    form = MemberForm(obj=member)
    _populate_choices(form)
    if request.method == "GET":
        form.care_cell_id.data = member.care_cell_id or 0
    if form.validate_on_submit():
        _apply_form(form, member)
        _handle_photo(form, member, "individual")
        db.session.commit()
        flash("Member updated.", "success")
        return redirect(url_for("members.member_detail", member_id=member.id))
    return render_template("members/form.html", form=form, is_new=False, member=member)


@members_bp.route("/<int:member_id>/delete", methods=["POST"])
@login_required
@require_permission("members", "delete")
def member_delete(member_id):
    member = db.get_or_404(Member, member_id)
    db.session.delete(member)
    db.session.commit()
    flash("Member deleted.", "warning")
    return redirect(url_for("members.list_members"))


@members_bp.route("/<int:member_id>/documents", methods=["POST"])
@login_required
@require_permission("members", "edit")
def add_document(member_id):
    member = db.get_or_404(Member, member_id)
    form = DocumentForm()
    if form.validate_on_submit():
        try:
            path = save_document(form.document.data)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("members.member_detail", member_id=member.id))
        db.session.add(
            MemberDocument(
                member_id=member.id,
                document_type=form.document_type.data,
                file_name=form.document.data.filename,
                file_path=path,
            )
        )
        db.session.commit()
        flash("Document uploaded.", "success")
    return redirect(url_for("members.member_detail", member_id=member.id))


@members_bp.route("/<int:member_id>/training", methods=["POST"])
@login_required
@require_permission("members", "edit")
def add_training(member_id):
    member = db.get_or_404(Member, member_id)
    form = TrainingForm()
    form.course_id.choices = [
        (c.id, c.name) for c in TrainingCourse.query.order_by(TrainingCourse.name)
    ]
    if form.validate_on_submit():
        db.session.add(
            MemberTraining(
                member_id=member.id,
                course_id=form.course_id.data,
                completion_status=form.completion_status.data,
                completion_date=form.completion_date.data,
                certificate_number=form.certificate_number.data,
            )
        )
        db.session.commit()
        flash("Training record added.", "success")
    else:
        flash("Could not add training — check the form.", "error")
    return redirect(url_for("members.member_detail", member_id=member.id))


@members_bp.route("/media/<path:file_path>")
@login_required
def media(file_path):
    """Serve locally-stored uploads (photos/documents)."""
    from app.utils.storage import LocalStorageBackend

    backend = storage._get()
    if isinstance(backend, LocalStorageBackend):
        full = backend.abspath(file_path)
        if not full.exists():
            abort(404)
        return send_file(full)
    # Non-local backends return a direct/presigned URL
    return redirect(backend.url(file_path))


# --- helpers -----------------------------------------------------------
def _apply_form(form, member):
    skip = {"photo", "submit", "csrf_token", "care_cell_id"}
    for field in form:
        if field.name in skip:
            continue
        setattr(member, field.name, field.data)
    member.care_cell_id = form.care_cell_id.data or None


def _handle_photo(form, member, photo_type):
    if form.photo.data and form.photo.data.filename:
        try:
            path = save_photo(form.photo.data)
        except ValueError as exc:
            flash(str(exc), "error")
            return
        db.session.add(
            MemberPhoto(member_id=member.id, photo_type=photo_type, file_path=path)
        )
