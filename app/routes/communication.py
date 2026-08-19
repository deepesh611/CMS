from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.base import utcnow

from app.extensions import db
from app.forms.communication import CommunicationForm
from app.models.communication import (
    Communication,
    EmailLog,
    SMSLog,
    WhatsAppLog,
)
from app.models.member import Member
from app.utils.communication import send_email, send_sms, send_whatsapp
from app.utils.decorators import require_permission
from app.utils.file_upload import save_photo

communication_bp = Blueprint("communication", __name__, url_prefix="/communication")

SOCIAL_CHANNELS = {"Facebook", "Telegram", "Instagram", "YouTube"}


@communication_bp.route("/")
@login_required
@require_permission("communication", "view")
def index():
    items = Communication.query.order_by(Communication.created_at.desc()).all()
    return render_template("communication/index.html", communications=items)


@communication_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_permission("communication", "edit")
def compose():
    form = CommunicationForm()
    if form.validate_on_submit():
        comm = Communication(
            channel=form.channel.data,
            category=form.category.data,
            subject=form.subject.data,
            body=form.body.data,
            status="Draft",
        )
        if form.flyer.data and form.flyer.data.filename:
            try:
                comm.flyer_path = save_photo(form.flyer.data, folder="flyers")
            except ValueError as exc:
                flash(str(exc), "error")
        db.session.add(comm)
        db.session.commit()
        flash("Communication saved as draft.", "success")
        return redirect(
            url_for(
                "communication.detail",
                comm_id=comm.id,
                group=form.recipient_group.data,
            )
        )
    return render_template("communication/compose.html", form=form)


@communication_bp.route("/<int:comm_id>")
@login_required
@require_permission("communication", "view")
def detail(comm_id):
    comm = db.get_or_404(Communication, comm_id)
    group = request.args.get("group", "all")
    return render_template("communication/detail.html", comm=comm, group=group)


@communication_bp.route("/<int:comm_id>/send/<group>", methods=["POST"])
@login_required
@require_permission("communication", "send")
def send(comm_id, group):
    comm = db.get_or_404(Communication, comm_id)

    if comm.channel in SOCIAL_CHANNELS:
        flash(
            f"{comm.channel} publishing is a manual step — content is saved and "
            "ready to post. API auto-posting can be configured later.",
            "info",
        )
        comm.status = "Ready to Publish"
        db.session.commit()
        return redirect(url_for("communication.detail", comm_id=comm.id))

    recipients = _recipients_for(group, comm.channel)
    sent = 0
    for value in recipients:
        _dispatch(comm, value)
        sent += 1

    comm.status = "Sent"
    comm.sent_at = utcnow()
    db.session.commit()
    flash(f"Sent to {sent} recipient(s). See delivery log below.", "success")
    return redirect(url_for("communication.detail", comm_id=comm.id))


def _recipients_for(group, channel):
    members = Member.query.all()
    values = []
    for m in members:
        if channel == "Email":
            if m.email and (group in {"all", "email"}):
                values.append(m.email)
        elif channel == "SMS":
            if m.gsm_number and (group in {"all", "phone"}):
                values.append(m.gsm_number)
        elif channel == "WhatsApp":
            num = m.whatsapp_number or m.gsm_number
            if num and (group in {"all", "phone"}):
                values.append(num)
    return values


def _dispatch(comm, recipient):
    if comm.channel == "Email":
        ok, err = send_email(recipient, comm.subject or "(no subject)", comm.body)
        db.session.add(
            EmailLog(
                communication_id=comm.id,
                recipient=recipient,
                status="Sent" if ok else "Failed",
                error=err,
            )
        )
    elif comm.channel == "SMS":
        ok, sid, err = send_sms(recipient, comm.body)
        db.session.add(
            SMSLog(
                communication_id=comm.id,
                recipient=recipient,
                status="Sent" if ok else "Failed",
                provider_sid=sid,
                error=err,
            )
        )
    elif comm.channel == "WhatsApp":
        ok, sid, err = send_whatsapp(recipient, comm.body)
        db.session.add(
            WhatsAppLog(
                communication_id=comm.id,
                recipient=recipient,
                status="Sent" if ok else "Failed",
                provider_sid=sid,
                error=err,
            )
        )
