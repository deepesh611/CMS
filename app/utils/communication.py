"""Messaging providers: email (Flask-Mail) and SMS/WhatsApp (Twilio).

Set SMS_PROVIDER=log to log instead of sending (used in tests / when Twilio
credentials are absent).
"""
from flask import current_app

from app.extensions import mail


def send_email(recipient, subject, body):
    """Send an email. Returns (ok, error)."""
    try:
        from flask_mail import Message

        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True, None
    except Exception as exc:  # SMTP failures, bad config, etc.
        return False, str(exc)


def _twilio_client():
    from twilio.rest import Client

    sid = current_app.config["TWILIO_ACCOUNT_SID"]
    token = current_app.config["TWILIO_AUTH_TOKEN"]
    if not sid or not token:
        raise RuntimeError("Twilio credentials are not configured.")
    return Client(sid, token)


def send_sms(recipient, body):
    """Send an SMS via Twilio. Returns (ok, sid_or_none, error)."""
    if current_app.config["SMS_PROVIDER"] == "log":
        current_app.logger.info("SMS (log mode) to %s: %s", recipient, body)
        return True, "LOG", None
    try:
        client = _twilio_client()
        msg = client.messages.create(
            to=recipient,
            from_=current_app.config["TWILIO_FROM_NUMBER"],
            body=body,
        )
        return True, msg.sid, None
    except Exception as exc:
        return False, None, str(exc)


def send_whatsapp(recipient, body):
    """Send a WhatsApp message via Twilio. Returns (ok, sid_or_none, error)."""
    if current_app.config["SMS_PROVIDER"] == "log":
        current_app.logger.info("WhatsApp (log mode) to %s: %s", recipient, body)
        return True, "LOG", None
    try:
        client = _twilio_client()
        to = recipient if recipient.startswith("whatsapp:") else f"whatsapp:{recipient}"
        msg = client.messages.create(
            to=to,
            from_=current_app.config["TWILIO_WHATSAPP_FROM"],
            body=body,
        )
        return True, msg.sid, None
    except Exception as exc:
        return False, None, str(exc)
