from flask import (
    Blueprint,
    abort,
    render_template,
    request,
    send_file,
)
from flask_login import login_required
import io

from app.extensions import db
from app.utils.decorators import require_permission
from app.utils.import_export import export_csv, export_excel, export_json
from app.utils.reports import table_pdf

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _report_membership():
    from app.models.member import Member

    headers = ["Number", "Name", "Gender", "Age", "Phone", "Status", "Joined"]
    rows = [
        [m.member_number, m.full_name, m.gender or "", m.age if m.age is not None else "",
         m.gsm_number or "", m.membership_status or "", str(m.joining_date or "")]
        for m in Member.query.order_by(Member.last_name)
    ]
    return "Membership Report", headers, rows


def _report_birthdays():
    from app.models.member import Member

    headers = ["Name", "DOB", "Age", "Phone"]
    rows = [
        [m.full_name, str(m.dob or ""), m.age if m.age is not None else "", m.gsm_number or ""]
        for m in Member.query.filter(Member.dob.isnot(None)).order_by(Member.dob)
    ]
    return "Birthday Report", headers, rows


def _report_attendance():
    from sqlalchemy import func
    from app.models.events import Attendance, Event

    headers = ["Event", "Date", "Present", "Total"]
    q = (
        db.session.query(
            Event.name,
            Event.event_date,
            func.sum(db.case((Attendance.status == "Present", 1), else_=0)),
            func.count(Attendance.id),
        )
        .join(Attendance, Attendance.event_id == Event.id)
        .group_by(Event.id)
        .order_by(Event.event_date.desc())
    )
    rows = [[r[0], str(r[1] or ""), int(r[2] or 0), int(r[3] or 0)] for r in q.all()]
    return "Attendance Report", headers, rows


def _report_finance():
    from app.models.finance import Tithe, Offering, Donation

    headers = ["Type", "Date", "Amount", "Reference"]
    rows = []
    for t in Tithe.query.all():
        rows.append(["Tithe", str(t.payment_date or ""), float(t.amount),
                     t.member.full_name if t.member else "Anonymous"])
    for o in Offering.query.all():
        rows.append(["Offering", str(o.service_date or ""), float(o.amount),
                     o.service_type or ""])
    for d in Donation.query.all():
        rows.append(["Donation", str(d.donation_date or ""), float(d.amount),
                     d.purpose or ""])
    return "Financial Report", headers, rows


def _report_welfare():
    from app.models.finance import WelfareRequest

    headers = ["Member", "Type", "Amount", "Status", "Approved By"]
    rows = [
        [w.member.full_name if w.member else "", w.support_type or "",
         float(w.amount) if w.amount is not None else "", w.status, w.approved_by or ""]
        for w in WelfareRequest.query.all()
    ]
    return "Welfare Report", headers, rows


def _report_inventory():
    from app.models.inventory import InventoryItem

    headers = ["Code", "Name", "Category", "Value", "Status", "Next Maintenance"]
    rows = [
        [i.asset_code, i.asset_name, i.category or "",
         float(i.value) if i.value is not None else "", i.status,
         str(i.next_maintenance_date or "")]
        for i in InventoryItem.query.all()
    ]
    return "Inventory Report", headers, rows


def _report_visitors():
    from app.models.outreach import Visitor

    headers = ["Name", "Phone", "Visit Date", "Invited By", "Status"]
    rows = [
        [v.full_name, v.phone or "", str(v.visit_date or ""), v.invited_by or "",
         v.followup_status]
        for v in Visitor.query.all()
    ]
    return "Visitor Report", headers, rows


REPORTS = {
    "membership": _report_membership,
    "birthdays": _report_birthdays,
    "attendance": _report_attendance,
    "finance": _report_finance,
    "welfare": _report_welfare,
    "inventory": _report_inventory,
    "visitors": _report_visitors,
}

REPORT_LABELS = {
    "membership": "Membership",
    "birthdays": "Birthdays",
    "attendance": "Attendance",
    "finance": "Financial",
    "welfare": "Welfare",
    "inventory": "Inventory",
    "visitors": "Visitors",
}


@reports_bp.route("/")
@login_required
@require_permission("reports", "view")
def index():
    return render_template("reports/index.html", reports=REPORT_LABELS)


@reports_bp.route("/<report_key>")
@login_required
@require_permission("reports", "view")
def view(report_key):
    builder = REPORTS.get(report_key)
    if not builder:
        abort(404)
    title, headers, rows = builder()
    fmt = request.args.get("format")

    if fmt:
        if not _has_export_permission():
            abort(403)
        return _export(fmt, report_key, title, headers, rows)

    return render_template(
        "reports/view.html",
        title=title, headers=headers, rows=rows, report_key=report_key,
    )


def _has_export_permission():
    from flask_login import current_user

    return (
        current_user.has_permission("reports", "export")
        or (current_user.role and current_user.role.name
            in {"Super Administrator", "IT Administrator"})
    )


def _export(fmt, report_key, title, headers, rows):
    if fmt == "pdf":
        data = table_pdf(title, headers, rows)
        return send_file(io.BytesIO(data), mimetype="application/pdf",
                         as_attachment=True, download_name=f"{report_key}.pdf")
    dict_rows = [dict(zip(headers, r)) for r in rows]
    if fmt == "excel":
        data = export_excel(dict_rows, headers, sheet_name=report_key)
        return send_file(
            io.BytesIO(data),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True, download_name=f"{report_key}.xlsx",
        )
    if fmt == "csv":
        data = export_csv(dict_rows, headers)
        return send_file(io.BytesIO(data), mimetype="text/csv",
                         as_attachment=True, download_name=f"{report_key}.csv")
    if fmt == "json":
        data = export_json(dict_rows)
        return send_file(io.BytesIO(data), mimetype="application/json",
                         as_attachment=True, download_name=f"{report_key}.json")
    abort(400)
