"""Communications, delivery logs, Google Forms integration."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class Communication(TimestampMixin, db.Model):
    __tablename__ = "communications"

    id = db.Column("CommunicationID", db.Integer, primary_key=True)
    channel = db.Column("Channel", db.String(40))  # Email/SMS/WhatsApp/Facebook/...
    subject = db.Column("Subject", db.String(200))
    body = db.Column("Body", db.Text)
    category = db.Column("Category", db.String(80))  # Announcement/Devotion/Birthday/...
    scheduled_for = db.Column("ScheduledFor", db.DateTime)
    sent_at = db.Column("SentAt", db.DateTime)
    status = db.Column("Status", db.String(40), default="Draft")
    flyer_path = db.Column("FlyerPath", db.String(255))

    email_logs = db.relationship(
        "EmailLog", back_populates="communication", cascade="all, delete-orphan"
    )
    sms_logs = db.relationship(
        "SMSLog", back_populates="communication", cascade="all, delete-orphan"
    )
    whatsapp_logs = db.relationship(
        "WhatsAppLog", back_populates="communication", cascade="all, delete-orphan"
    )


class EmailLog(TimestampMixin, db.Model):
    __tablename__ = "email_logs"

    id = db.Column("EmailID", db.Integer, primary_key=True)
    communication_id = db.Column(
        "CommunicationID",
        db.Integer,
        db.ForeignKey("communications.CommunicationID"),
        nullable=False,
    )
    recipient = db.Column("Recipient", db.String(120))
    status = db.Column("Status", db.String(40), default="Queued")
    error = db.Column("Error", db.String(255))
    sent_at = db.Column("SentAt", db.DateTime, default=utcnow)

    communication = db.relationship("Communication", back_populates="email_logs")


class SMSLog(TimestampMixin, db.Model):
    __tablename__ = "sms_logs"

    id = db.Column("SMSID", db.Integer, primary_key=True)
    communication_id = db.Column(
        "CommunicationID",
        db.Integer,
        db.ForeignKey("communications.CommunicationID"),
        nullable=False,
    )
    recipient = db.Column("Recipient", db.String(40))
    status = db.Column("Status", db.String(40), default="Queued")
    provider_sid = db.Column("ProviderSid", db.String(80))
    error = db.Column("Error", db.String(255))
    sent_at = db.Column("SentAt", db.DateTime, default=utcnow)

    communication = db.relationship("Communication", back_populates="sms_logs")


class WhatsAppLog(TimestampMixin, db.Model):
    __tablename__ = "whatsapp_logs"

    id = db.Column("WhatsAppID", db.Integer, primary_key=True)
    communication_id = db.Column(
        "CommunicationID",
        db.Integer,
        db.ForeignKey("communications.CommunicationID"),
        nullable=False,
    )
    recipient = db.Column("Recipient", db.String(40))
    status = db.Column("Status", db.String(40), default="Queued")
    provider_sid = db.Column("ProviderSid", db.String(80))
    error = db.Column("Error", db.String(255))
    sent_at = db.Column("SentAt", db.DateTime, default=utcnow)

    communication = db.relationship("Communication", back_populates="whatsapp_logs")


class GoogleForm(TimestampMixin, db.Model):
    __tablename__ = "google_forms"

    id = db.Column("FormID", db.Integer, primary_key=True)
    name = db.Column("FormName", db.String(150), nullable=False)
    form_url = db.Column("FormURL", db.String(255))
    sheet_id = db.Column("SheetID", db.String(120))
    field_mapping = db.Column("FieldMapping", db.Text)  # JSON: form col -> db col
    target_module = db.Column("TargetModule", db.String(80))

    responses = db.relationship(
        "FormResponse", back_populates="form", cascade="all, delete-orphan"
    )


class FormResponse(TimestampMixin, db.Model):
    __tablename__ = "form_responses"

    id = db.Column("ResponseID", db.Integer, primary_key=True)
    form_id = db.Column(
        "FormID", db.Integer, db.ForeignKey("google_forms.FormID"), nullable=False
    )
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))
    raw_data = db.Column("RawData", db.Text)  # JSON payload
    imported = db.Column("Imported", db.Boolean, default=False)

    form = db.relationship("GoogleForm", back_populates="responses")
    member = db.relationship("Member")
