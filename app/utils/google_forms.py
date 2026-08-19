"""Google Forms / Sheets import.

Reads form responses from a linked Google Sheet (form responses destination)
using a service account, and stores raw responses. Field mapping (JSON on the
GoogleForm record) maps sheet columns to member fields for optional promotion
into the Members table.

Requires GOOGLE_SERVICE_ACCOUNT_JSON to point at a service-account key file and
the sheet shared with that service account.
"""
import json

from flask import current_app

from app.extensions import db
from app.models.communication import FormResponse, GoogleForm


def _sheets_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    key_path = current_app.config.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_path:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured.")
    creds = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    return build("sheets", "v4", credentials=creds)


def import_form_responses(form_id, sheet_range="A1:Z10000"):
    """Pull rows from the linked sheet into FormResponse rows.
    Returns the number of new responses imported."""
    form = db.session.get(GoogleForm, form_id)
    if not form or not form.sheet_id:
        raise ValueError("Form has no linked Google Sheet.")

    service = _sheets_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=form.sheet_id, range=sheet_range)
        .execute()
    )
    rows = result.get("values", [])
    if not rows:
        return 0

    header, *data_rows = rows
    existing = FormResponse.query.filter_by(form_id=form.id).count()
    new_count = 0
    for row in data_rows[existing:]:
        record = dict(zip(header, row))
        db.session.add(
            FormResponse(
                form_id=form.id,
                raw_data=json.dumps(record),
                imported=False,
            )
        )
        new_count += 1
    db.session.commit()
    return new_count
