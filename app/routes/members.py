import csv
import io
from datetime import datetime

from flask import (
    Blueprint,
    Response,
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


# ---------------------------------------------------------------------------
# Bulk CSV import
# ---------------------------------------------------------------------------

# All columns present in the template (order matters for the downloaded file)
_CSV_COLUMNS = [
    "first_name", "middle_name", "last_name",
    "dob",
    "gender", "nationality", "marital_status",
    "email", "personal_email",
    "gsm_number", "whatsapp_number",
    "address_line", "address_state", "address_country", "address_zip",
    "employed",
    "occupation", "employer_name", "place_of_work", "professional_category",
    "baptism_date", "joining_date",
    "membership_status",
    "mother_church_name",
    "mother_church_address_line", "mother_church_address_state",
    "mother_church_address_country", "mother_church_address_zip",
]

_SAMPLE_ROW = {
    "first_name": "John",
    "middle_name": "Michael",
    "last_name": "Doe",
    "dob": "15/06/1990",
    "gender": "Male",
    "nationality": "Ghanaian",
    "marital_status": "Married",
    "email": "john.doe@example.com",
    "personal_email": "",
    "gsm_number": "+233201234567",
    "whatsapp_number": "+233201234567",
    "address_line": "12 Accra Street",
    "address_state": "Greater Accra",
    "address_country": "Ghana",
    "address_zip": "00233",
    "employed": "TRUE",
    "occupation": "Engineer",
    "employer_name": "Acme Ltd",
    "place_of_work": "Accra",
    "professional_category": "Professional",
    "baptism_date": "10/04/2015",
    "joining_date": "01/01/2016",
    "membership_status": "Active",
    "mother_church_name": "Grace Chapel",
    "mother_church_address_line": "5 Church Road",
    "mother_church_address_state": "Ashanti",
    "mother_church_address_country": "Ghana",
    "mother_church_address_zip": "00200",
}


def _parse_date(value, fmt="%d/%m/%Y"):
    """Return a date object or raise ValueError."""
    return datetime.strptime(value.strip(), fmt).date()


def _build_address(row, prefix=""):
    """Combine address sub-columns into a single address string."""
    line = row.get(f"{prefix}address_line", "").strip()
    state = row.get(f"{prefix}address_state", "").strip()
    country = row.get(f"{prefix}address_country", "").strip()
    zipcode = row.get(f"{prefix}address_zip", "").strip()
    parts = [p for p in [line, state, zipcode, country] if p]
    return ", ".join(parts) if parts else None


def _validate_row(row, row_num):
    """Return list of error strings for a CSV row (empty = row is valid)."""
    errors = []

    first = row.get("first_name", "").strip()
    last = row.get("last_name", "").strip()
    dob_raw = row.get("dob", "").strip()

    if not first:
        errors.append("Missing first_name")
    if not last:
        errors.append("Missing last_name")
    if not dob_raw:
        errors.append("Missing dob")
    else:
        try:
            _parse_date(dob_raw)
        except ValueError:
            errors.append(f"Invalid dob format '{dob_raw}' — expected DD/MM/YYYY")

    # Email validation
    for field_name in ("email", "personal_email"):
        val = row.get(field_name, "").strip()
        if val and "@" not in val:
            errors.append(f"Invalid {field_name}: missing '@'")

    # Optional date fields
    for date_field in ("baptism_date", "joining_date"):
        val = row.get(date_field, "").strip()
        if val:
            try:
                _parse_date(val)
            except ValueError:
                errors.append(f"Invalid {date_field} format '{val}' — expected DD/MM/YYYY")

    return errors


@members_bp.route("/import", methods=["GET", "POST"])
@login_required
@require_permission("members", "edit")
def bulk_import():
    if request.method == "GET":
        return render_template("members/bulk_import.html")

    # ── POST: process uploaded file ──────────────────────────────────────────
    file = request.files.get("csv_file")
    if not file or not file.filename:
        flash("Please select a CSV file to upload.", "warning")
        return redirect(url_for("members.bulk_import"))

    if not file.filename.lower().endswith(".csv"):
        flash("Only .csv files are accepted.", "danger")
        return redirect(url_for("members.bulk_import"))

    stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
    reader = csv.DictReader(stream)

    good_rows = []   # list of Member objects ready to insert
    bad_rows = []    # list of {row_num, name, dob, reasons}

    for row_num, row in enumerate(reader, start=2):  # row 1 = header
        errors = _validate_row(row, row_num)

        first = row.get("first_name", "").strip()
        last = row.get("last_name", "").strip()
        dob_raw = row.get("dob", "").strip()
        dob = None
        if dob_raw and not any("dob" in e.lower() for e in errors):
            dob = _parse_date(dob_raw)

        # Duplicate check (only when we have enough info to query)
        if not errors and first and last and dob:
            existing = Member.query.filter(
                Member.first_name.ilike(first),
                Member.last_name.ilike(last),
                Member.dob == dob,
            ).first()
            if existing:
                errors.append(
                    f"Duplicate: member '{existing.full_name}' ({existing.member_number}) already exists"
                )

        if errors:
            bad_rows.append({
                "row_num": row_num,
                "name": f"{first} {last}".strip() or "—",
                "dob": dob_raw or "—",
                "reasons": errors,
            })
            continue

        # Build member object
        member = Member(member_number=_next_member_number())
        member.first_name = first
        member.middle_name = row.get("middle_name", "").strip() or None
        member.last_name = last
        member.dob = dob
        member.gender = row.get("gender", "").strip() or None
        member.nationality = row.get("nationality", "").strip() or None
        member.marital_status = row.get("marital_status", "").strip() or None
        member.email = row.get("email", "").strip() or None
        member.personal_email = row.get("personal_email", "").strip() or None
        member.gsm_number = row.get("gsm_number", "").strip() or None
        member.whatsapp_number = row.get("whatsapp_number", "").strip() or None
        member.address = _build_address(row) or None
        member.employed = row.get("employed", "").strip().upper() == "TRUE"
        member.occupation = row.get("occupation", "").strip() or None
        member.employer_name = row.get("employer_name", "").strip() or None
        member.place_of_work = row.get("place_of_work", "").strip() or None
        member.professional_category = row.get("professional_category", "").strip() or None
        member.membership_status = row.get("membership_status", "").strip() or "Active"
        member.mother_church_name = row.get("mother_church_name", "").strip() or None
        member.mother_church_address = _build_address(row, "mother_church_") or None
        member.mother_church_country = row.get("mother_church_address_country", "").strip() or None

        bdate = row.get("baptism_date", "").strip()
        member.baptism_date = _parse_date(bdate) if bdate else None
        jdate = row.get("joining_date", "").strip()
        member.joining_date = _parse_date(jdate) if jdate else None

        good_rows.append(member)
        db.session.add(member)

    db.session.commit()

    return render_template(
        "members/bulk_import.html",
        imported=len(good_rows),
        bad_rows=bad_rows,
        show_results=True,
    )


@members_bp.route("/import/template")
@login_required
@require_permission("members", "edit")
def import_template():
    """Stream a CSV template file with headers + one sample row."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=_CSV_COLUMNS)
    writer.writeheader()
    writer.writerow(_SAMPLE_ROW)
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=member_import_template.csv"},
    )


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
