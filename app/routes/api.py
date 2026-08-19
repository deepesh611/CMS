"""Minimal read-oriented REST API (JSON). Authenticated via session login.

All endpoints require an authenticated user and the matching module 'view'
permission. Intended for integrations and the future migration to a richer API.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.extensions import db
from app.models.member import Member
from app.utils.decorators import require_permission

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.route("/members")
@login_required
@require_permission("members", "view")
def members():
    q = request.args.get("q", "").strip()
    query = Member.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Member.first_name.ilike(like), Member.last_name.ilike(like))
        )
    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=50, error_out=False)
    return jsonify(
        {
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
            "items": [
                {
                    "id": m.id,
                    "member_number": m.member_number,
                    "name": m.full_name,
                    "gender": m.gender,
                    "age": m.age,
                    "email": m.email,
                    "phone": m.gsm_number,
                    "membership_status": m.membership_status,
                }
                for m in pagination.items
            ],
        }
    )


@api_bp.route("/members/<int:member_id>")
@login_required
@require_permission("members", "view")
def member(member_id):
    m = db.get_or_404(Member, member_id)
    return jsonify(
        {
            "id": m.id,
            "member_number": m.member_number,
            "name": m.full_name,
            "gender": m.gender,
            "dob": m.dob.isoformat() if m.dob else None,
            "age": m.age,
            "email": m.email,
            "phone": m.gsm_number,
            "marital_status": m.marital_status,
            "membership_status": m.membership_status,
            "children": [
                {"name": c.full_name, "dob": c.dob.isoformat() if c.dob else None}
                for c in m.children
            ],
        }
    )
