from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.forms.finance import (
    DonationForm,
    MissionForm,
    MissionSupportForm,
    OfferingForm,
    TitheForm,
)
from app.models.finance import (
    Donation,
    Mission,
    MissionSupport,
    Offering,
    Tithe,
)
from app.models.member import Member
from app.utils.decorators import require_permission

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


def _member_choices(optional=True):
    base = [(0, "—")] if optional else []
    return base + [
        (m.id, f"{m.full_name} ({m.member_number})")
        for m in Member.query.order_by(Member.last_name)
    ]


@finance_bp.route("/")
@login_required
@require_permission("finance", "view")
def dashboard():
    month_start = date.today().replace(day=1)
    tithes = float(
        db.session.query(func.coalesce(func.sum(Tithe.amount), 0)).scalar() or 0
    )
    offerings = float(
        db.session.query(func.coalesce(func.sum(Offering.amount), 0)).scalar() or 0
    )
    donations = float(
        db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar() or 0
    )
    missions = float(
        db.session.query(func.coalesce(func.sum(MissionSupport.amount), 0)).scalar() or 0
    )

    # Monthly tithe trend (last 6 months) for the chart
    trend = (
        db.session.query(
            func.strftime("%Y-%m", Tithe.payment_date).label("month"),
            func.sum(Tithe.amount),
        )
        .filter(Tithe.payment_date.isnot(None))
        .group_by("month")
        .order_by("month")
        .limit(12)
        .all()
    )
    trend_labels = [t[0] for t in trend]
    trend_values = [float(t[1]) for t in trend]

    return render_template(
        "finance/dashboard.html",
        totals={"tithes": tithes, "offerings": offerings,
                "donations": donations, "missions": missions},
        trend_labels=trend_labels,
        trend_values=trend_values,
    )


# ------------------------------------------------------------------ Tithes
@finance_bp.route("/tithes")
@login_required
@require_permission("finance", "view")
def tithes():
    items = Tithe.query.order_by(Tithe.payment_date.desc()).limit(200).all()
    return render_template("finance/tithes.html", tithes=items)


@finance_bp.route("/tithes/new", methods=["GET", "POST"])
@login_required
@require_permission("finance", "edit")
def tithe_create():
    form = TitheForm()
    form.member_id.choices = _member_choices()
    if form.validate_on_submit():
        db.session.add(
            Tithe(
                member_id=form.member_id.data or None,
                amount=form.amount.data,
                payment_date=form.payment_date.data or date.today(),
                payment_method=form.payment_method.data,
            )
        )
        db.session.commit()
        flash("Tithe recorded.", "success")
        return redirect(url_for("finance.tithes"))
    return render_template("finance/tithe_form.html", form=form)


# ---------------------------------------------------------------- Offerings
@finance_bp.route("/offerings")
@login_required
@require_permission("finance", "view")
def offerings():
    items = Offering.query.order_by(Offering.service_date.desc()).limit(200).all()
    return render_template("finance/offerings.html", offerings=items)


@finance_bp.route("/offerings/new", methods=["GET", "POST"])
@login_required
@require_permission("finance", "edit")
def offering_create():
    form = OfferingForm()
    if form.validate_on_submit():
        db.session.add(
            Offering(
                amount=form.amount.data,
                service_date=form.service_date.data or date.today(),
                service_type=form.service_type.data,
            )
        )
        db.session.commit()
        flash("Offering recorded.", "success")
        return redirect(url_for("finance.offerings"))
    return render_template("finance/offering_form.html", form=form)


# ---------------------------------------------------------------- Donations
@finance_bp.route("/donations")
@login_required
@require_permission("finance", "view")
def donations():
    items = Donation.query.order_by(Donation.donation_date.desc()).limit(200).all()
    return render_template("finance/donations.html", donations=items)


@finance_bp.route("/donations/new", methods=["GET", "POST"])
@login_required
@require_permission("finance", "edit")
def donation_create():
    form = DonationForm()
    form.member_id.choices = _member_choices()
    if form.validate_on_submit():
        db.session.add(
            Donation(
                member_id=form.member_id.data or None,
                donor_name=form.donor_name.data,
                amount=form.amount.data,
                purpose=form.purpose.data,
                donation_date=form.donation_date.data or date.today(),
            )
        )
        db.session.commit()
        flash("Donation recorded.", "success")
        return redirect(url_for("finance.donations"))
    return render_template("finance/donation_form.html", form=form)


# ----------------------------------------------------------------- Missions
@finance_bp.route("/missions", methods=["GET", "POST"])
@login_required
@require_permission("finance", "view")
def missions():
    items = Mission.query.order_by(Mission.name).all()
    return render_template("finance/missions.html", missions=items)


@finance_bp.route("/missions/new", methods=["GET", "POST"])
@login_required
@require_permission("finance", "edit")
def mission_create():
    form = MissionForm()
    if form.validate_on_submit():
        m = Mission(
            name=form.name.data,
            country=form.country.data,
            mission_type=form.mission_type.data,
        )
        db.session.add(m)
        db.session.commit()
        flash("Mission created.", "success")
        return redirect(url_for("finance.mission_detail", mission_id=m.id))
    return render_template("finance/mission_form.html", form=form)


@finance_bp.route("/missions/<int:mission_id>", methods=["GET", "POST"])
@login_required
@require_permission("finance", "view")
def mission_detail(mission_id):
    mission = db.get_or_404(Mission, mission_id)
    form = MissionSupportForm()
    form.mission_id.choices = [(mission.id, mission.name)]
    if form.validate_on_submit():
        db.session.add(
            MissionSupport(
                mission_id=mission.id,
                amount=form.amount.data,
                support_date=form.support_date.data or date.today(),
            )
        )
        db.session.commit()
        flash("Support recorded.", "success")
        return redirect(url_for("finance.mission_detail", mission_id=mission.id))
    return render_template("finance/mission_detail.html", mission=mission, form=form)
