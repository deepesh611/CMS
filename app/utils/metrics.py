"""Dashboard KPI aggregation."""
from datetime import date

from sqlalchemy import func

from app.extensions import db


def dashboard_kpis():
    from app.models.finance import Tithe, Offering, WelfareRequest
    from app.models.member import Member

    today = date.today()
    month_start = today.replace(day=1)

    total_members = db.session.query(func.count(Member.id)).scalar() or 0
    new_this_month = (
        db.session.query(func.count(Member.id))
        .filter(Member.joining_date >= month_start)
        .scalar()
        or 0
    )
    tithes_month = (
        db.session.query(func.coalesce(func.sum(Tithe.amount), 0))
        .filter(Tithe.payment_date >= month_start)
        .scalar()
        or 0
    )
    offerings_month = (
        db.session.query(func.coalesce(func.sum(Offering.amount), 0))
        .filter(Offering.service_date >= month_start)
        .scalar()
        or 0
    )
    open_welfare = (
        db.session.query(func.count(WelfareRequest.id))
        .filter(WelfareRequest.status.notin_(["Approved", "Rejected", "Closed"]))
        .scalar()
        or 0
    )

    return {
        "total_members": total_members,
        "new_this_month": new_this_month,
        "giving_month": float(tithes_month) + float(offerings_month),
        "open_welfare": open_welfare,
    }
