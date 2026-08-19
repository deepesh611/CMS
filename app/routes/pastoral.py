from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.pastoral import (
    BabyDedicationForm,
    CounsellingCaseForm,
    CounsellingFollowupForm,
    PrayerRequestForm,
    WelfareRequestForm,
)
from app.models.events import Pastor
from app.models.finance import WelfareRequest
from app.models.member import Child, Member
from app.models.pastoral import (
    BabyDedication,
    CounsellingCase,
    CounsellingFollowup,
    PrayerRequest,
)
from app.utils.decorators import require_permission

pastoral_bp = Blueprint("pastoral", __name__, url_prefix="/pastoral")


def _member_choices(optional=True):
    base = [(0, "—")] if optional else []
    return base + [
        (m.id, f"{m.full_name} ({m.member_number})")
        for m in Member.query.order_by(Member.last_name)
    ]


def _pastor_choices():
    choices = [(0, "—")]
    for p in Pastor.query.all():
        label = p.member.full_name if p.member else (p.position or f"Pastor #{p.id}")
        choices.append((p.id, label))
    return choices


def _can_view_confidential(case):
    role = current_user.role.name if current_user.role else ""
    if role in {"Super Administrator", "Senior Pastor"}:
        return True
    return bool(
        current_user.member_id and current_user.member_id == case.counsellor_id
    )


# --------------------------------------------------------------- Counselling
@pastoral_bp.route("/counselling")
@login_required
@require_permission("counselling", "view")
def counselling():
    cases = CounsellingCase.query.order_by(CounsellingCase.session_date.desc()).all()
    return render_template("pastoral/counselling.html", cases=cases)


@pastoral_bp.route("/counselling/new", methods=["GET", "POST"])
@login_required
@require_permission("counselling", "edit")
def counselling_create():
    form = CounsellingCaseForm()
    form.member_id.choices = _member_choices()
    form.counsellor_id.choices = _member_choices()
    if form.validate_on_submit():
        case = CounsellingCase(
            member_id=form.member_id.data or None,
            counsellor_id=form.counsellor_id.data or None,
            case_type=form.case_type.data,
            session_date=form.session_date.data,
            summary=form.summary.data,
            confidential_notes=form.confidential_notes.data,
            status=form.status.data,
        )
        db.session.add(case)
        db.session.commit()
        flash("Counselling case created.", "success")
        return redirect(url_for("pastoral.counselling_detail", case_id=case.id))
    return render_template("pastoral/counselling_form.html", form=form, is_new=True)


@pastoral_bp.route("/counselling/<int:case_id>", methods=["GET", "POST"])
@login_required
@require_permission("counselling", "view")
def counselling_detail(case_id):
    case = db.get_or_404(CounsellingCase, case_id)
    form = CounsellingFollowupForm()
    form.assigned_counsellor_id.choices = _member_choices()
    if form.validate_on_submit():
        if not current_user.has_permission("counselling", "edit"):
            abort(403)
        db.session.add(
            CounsellingFollowup(
                case_id=case.id,
                followup_date=form.followup_date.data,
                assigned_counsellor_id=form.assigned_counsellor_id.data or None,
                reminder=form.reminder.data,
                notes=form.notes.data,
            )
        )
        db.session.commit()
        flash("Follow-up added.", "success")
        return redirect(url_for("pastoral.counselling_detail", case_id=case.id))
    return render_template(
        "pastoral/counselling_detail.html",
        case=case,
        form=form,
        can_view_confidential=_can_view_confidential(case),
    )


# -------------------------------------------------------------- Prayer requests
@pastoral_bp.route("/prayer")
@login_required
@require_permission("prayer", "view")
def prayer_requests():
    items = PrayerRequest.query.order_by(PrayerRequest.created_at.desc()).all()
    return render_template("pastoral/prayer.html", requests=items)


@pastoral_bp.route("/prayer/new", methods=["GET", "POST"])
@login_required
@require_permission("prayer", "edit")
def prayer_create():
    form = PrayerRequestForm()
    form.member_id.choices = _member_choices()
    if form.validate_on_submit():
        pr = PrayerRequest(
            member_id=form.member_id.data or None,
            request_details=form.request_details.data,
            category=form.category.data,
            assigned_team=form.assigned_team.data,
            status=form.status.data,
            testimony=form.testimony.data,
        )
        db.session.add(pr)
        db.session.commit()
        flash("Prayer request recorded.", "success")
        return redirect(url_for("pastoral.prayer_requests"))
    return render_template("pastoral/prayer_form.html", form=form, is_new=True)


@pastoral_bp.route("/prayer/<int:req_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("prayer", "edit")
def prayer_edit(req_id):
    pr = db.get_or_404(PrayerRequest, req_id)
    form = PrayerRequestForm(obj=pr)
    form.member_id.choices = _member_choices()
    if form.validate_on_submit():
        pr.member_id = form.member_id.data or None
        pr.request_details = form.request_details.data
        pr.category = form.category.data
        pr.assigned_team = form.assigned_team.data
        pr.status = form.status.data
        pr.testimony = form.testimony.data
        db.session.commit()
        flash("Prayer request updated.", "success")
        return redirect(url_for("pastoral.prayer_requests"))
    return render_template("pastoral/prayer_form.html", form=form, is_new=False)


# -------------------------------------------------------------- Baby dedications
@pastoral_bp.route("/dedications")
@login_required
@require_permission("counselling", "view")
def dedications():
    items = BabyDedication.query.order_by(BabyDedication.dedication_date.desc()).all()
    return render_template("pastoral/dedications.html", dedications=items)


@pastoral_bp.route("/dedications/new", methods=["GET", "POST"])
@login_required
@require_permission("counselling", "edit")
def dedication_create():
    form = BabyDedicationForm()
    form.child_id.choices = [
        (c.id, c.full_name) for c in Child.query.order_by(Child.first_name)
    ] or [(0, "No children on file")]
    form.pastor_id.choices = _pastor_choices()
    if form.validate_on_submit():
        d = BabyDedication(
            child_id=form.child_id.data,
            dedication_date=form.dedication_date.data,
            pastor_id=form.pastor_id.data or None,
            certificate_issued=form.certificate_issued.data,
        )
        db.session.add(d)
        db.session.commit()
        flash("Baby dedication recorded.", "success")
        return redirect(url_for("pastoral.dedications"))
    return render_template("pastoral/dedication_form.html", form=form)


# --------------------------------------------------------------------- Welfare
@pastoral_bp.route("/welfare")
@login_required
@require_permission("welfare", "view")
def welfare():
    items = WelfareRequest.query.order_by(WelfareRequest.created_at.desc()).all()
    return render_template("pastoral/welfare.html", requests=items)


@pastoral_bp.route("/welfare/new", methods=["GET", "POST"])
@login_required
@require_permission("welfare", "edit")
def welfare_create():
    form = WelfareRequestForm()
    form.member_id.choices = _member_choices(optional=False)
    if form.validate_on_submit():
        w = WelfareRequest(
            member_id=form.member_id.data,
            support_type=form.support_type.data,
            amount=form.amount.data,
            status=form.status.data,
            approved_by=form.approved_by.data,
            followup_actions=form.followup_actions.data,
        )
        db.session.add(w)
        db.session.commit()
        flash("Welfare request created.", "success")
        return redirect(url_for("pastoral.welfare"))
    return render_template("pastoral/welfare_form.html", form=form, is_new=True)


@pastoral_bp.route("/welfare/<int:welfare_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("welfare", "edit")
def welfare_edit(welfare_id):
    w = db.get_or_404(WelfareRequest, welfare_id)
    form = WelfareRequestForm(obj=w)
    form.member_id.choices = _member_choices(optional=False)
    if form.validate_on_submit():
        # Approving requires the 'approve' action
        if form.status.data == "Approved" and not (
            current_user.has_permission("welfare", "approve")
            or (current_user.role and current_user.role.name
                in {"Super Administrator", "Senior Pastor", "Finance Officer"})
        ):
            flash("You do not have permission to approve welfare requests.", "error")
            return redirect(url_for("pastoral.welfare_edit", welfare_id=w.id))
        w.member_id = form.member_id.data
        w.support_type = form.support_type.data
        w.amount = form.amount.data
        w.status = form.status.data
        w.approved_by = form.approved_by.data
        w.followup_actions = form.followup_actions.data
        db.session.commit()
        flash("Welfare request updated.", "success")
        return redirect(url_for("pastoral.welfare"))
    return render_template("pastoral/welfare_form.html", form=form, is_new=False)
