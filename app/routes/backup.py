from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required

from app.extensions import db
from app.models.system import Backup
from app.utils.backup import create_backup, restore_backup, verify_backup
from app.utils.decorators import require_permission

backup_bp = Blueprint("backup", __name__, url_prefix="/backup")


@backup_bp.route("/")
@login_required
@require_permission("backup", "view")
def index():
    backups = Backup.query.order_by(Backup.backup_date.desc()).all()
    return render_template("backup/index.html", backups=backups)


@backup_bp.route("/create", methods=["POST"])
@login_required
@require_permission("backup", "edit")
def create():
    record = create_backup(backup_type="Manual")
    flash(f"Backup created: {Path(record.file_path).name}", "success")
    return redirect(url_for("backup.index"))


@backup_bp.route("/<int:backup_id>/download")
@login_required
@require_permission("backup", "view")
def download(backup_id):
    record = db.get_or_404(Backup, backup_id)
    path = Path(record.file_path)
    if not path.exists():
        flash("Backup file not found on disk.", "error")
        return redirect(url_for("backup.index"))
    return send_file(path, as_attachment=True, download_name=path.name)


@backup_bp.route("/<int:backup_id>/verify", methods=["POST"])
@login_required
@require_permission("backup", "edit")
def verify(backup_id):
    record = db.get_or_404(Backup, backup_id)
    record.verified = verify_backup(Path(record.file_path))
    db.session.commit()
    flash("Backup verified." if record.verified else "Backup is corrupt!",
          "success" if record.verified else "error")
    return redirect(url_for("backup.index"))


@backup_bp.route("/<int:backup_id>/restore", methods=["POST"])
@login_required
@require_permission("backup", "edit")
def restore(backup_id):
    record = db.get_or_404(Backup, backup_id)
    ok, message = restore_backup(record.file_path)
    flash(message, "success" if ok else "error")
    return redirect(url_for("backup.index"))
