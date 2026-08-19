"""System-level models: backups, audit logs, and dynamic custom fields."""
from app.extensions import db
from app.models.base import TimestampMixin, utcnow


class Backup(TimestampMixin, db.Model):
    __tablename__ = "backups"

    id = db.Column("BackupID", db.Integer, primary_key=True)
    backup_date = db.Column("BackupDate", db.DateTime, default=utcnow)
    backup_type = db.Column("BackupType", db.String(40))  # Daily/Weekly/Monthly/Manual
    file_path = db.Column("FilePath", db.String(255))
    size_bytes = db.Column("SizeBytes", db.BigInteger)
    verified = db.Column("Verified", db.Boolean, default=False)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column("AuditID", db.Integer, primary_key=True)
    user_id = db.Column("UserID", db.Integer, db.ForeignKey("users.UserID"))
    action = db.Column("Action", db.String(40))  # INSERT/UPDATE/DELETE
    table_name = db.Column("TableName", db.String(80))
    record_id = db.Column("RecordID", db.String(40))
    changes = db.Column("Changes", db.Text)  # JSON diff
    action_date = db.Column("ActionDate", db.DateTime, default=utcnow, index=True)

    user = db.relationship("User")


class CustomField(TimestampMixin, db.Model):
    """Dynamic form builder: extra fields IT Admin can add per module."""

    __tablename__ = "custom_fields"

    id = db.Column("FieldID", db.Integer, primary_key=True)
    module = db.Column("Module", db.String(80), nullable=False, index=True)
    field_name = db.Column("FieldName", db.String(80), nullable=False)
    field_label = db.Column("FieldLabel", db.String(120))
    field_type = db.Column("FieldType", db.String(40), default="text")
    required = db.Column("Required", db.Boolean, default=False)
    options = db.Column("Options", db.Text)  # JSON for select fields
    sort_order = db.Column("SortOrder", db.Integer, default=0)


class CustomFieldValue(TimestampMixin, db.Model):
    __tablename__ = "custom_field_values"

    id = db.Column("ValueID", db.Integer, primary_key=True)
    field_id = db.Column(
        "FieldID", db.Integer, db.ForeignKey("custom_fields.FieldID"), nullable=False
    )
    record_id = db.Column("RecordID", db.Integer, nullable=False)
    value = db.Column("Value", db.Text)

    field = db.relationship("CustomField")
