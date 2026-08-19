"""Automatic audit logging via SQLAlchemy session events.

Every INSERT/UPDATE/DELETE on a mapped model (except AuditLog itself) is
recorded with the acting user, table, record id, and a JSON diff.

Pattern (from SQLAlchemy's versioned-history recipe): build AuditLog objects
inside `before_flush` and add them to the session. They are flushed as part of
the *same* flush cycle, so nothing is lost — including changes made in the
final flush of a commit. AuditLog itself is skipped to avoid recursion.
"""
import json
from datetime import date, datetime
from decimal import Decimal

from flask import has_request_context
from flask_login import current_user
from sqlalchemy import event, inspect

from app.extensions import db


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def _current_user_id():
    if has_request_context():
        try:
            if current_user and current_user.is_authenticated:
                return current_user.id
        except Exception:
            pass
    return None


def _changed_fields(obj):
    changes = {}
    for attr in inspect(obj).attrs:
        hist = attr.load_history()
        if hist.has_changes():
            changes[attr.key] = {
                "old": hist.deleted[0] if hist.deleted else None,
                "new": hist.added[0] if hist.added else None,
            }
    return changes


def _new_values(obj):
    values = {}
    for attr in inspect(obj).attrs:
        # relationships expose .value differently; only capture column attrs
        try:
            val = getattr(obj, attr.key)
        except Exception:
            continue
        if isinstance(val, (str, int, float, bool, type(None), datetime, date, Decimal)):
            values[attr.key] = val
    return values


def _record_id(obj):
    identity = inspect(obj).identity
    if identity:
        return ",".join(str(p) for p in identity)
    val = getattr(obj, "id", None)
    return str(val) if val is not None else None


def init_audit(app):
    from app.models.system import AuditLog

    @event.listens_for(db.session, "before_flush")
    def before_flush(session, flush_context, instances):
        uid = _current_user_id()
        pending = []

        for obj in session.new:
            if isinstance(obj, AuditLog):
                continue
            pending.append(
                AuditLog(
                    user_id=uid,
                    action="INSERT",
                    table_name=obj.__tablename__,
                    record_id=None,  # PK not assigned until after flush
                    changes=json.dumps(_new_values(obj), default=_json_default),
                )
            )

        for obj in session.dirty:
            if isinstance(obj, AuditLog) or not session.is_modified(obj):
                continue
            changes = _changed_fields(obj)
            if changes:
                pending.append(
                    AuditLog(
                        user_id=uid,
                        action="UPDATE",
                        table_name=obj.__tablename__,
                        record_id=_record_id(obj),
                        changes=json.dumps(changes, default=_json_default),
                    )
                )

        for obj in session.deleted:
            if isinstance(obj, AuditLog):
                continue
            pending.append(
                AuditLog(
                    user_id=uid,
                    action="DELETE",
                    table_name=obj.__tablename__,
                    record_id=_record_id(obj),
                    changes=None,
                )
            )

        for entry in pending:
            session.add(entry)
