"""Backup and restore.

For SQLite: copies the database file plus zips the uploads directory into the
backup folder (configurable path — local drive, external drive, or network
share via APP_DATA_DIR / BACKUP_DIR). For non-SQLite databases the DB dump is
skipped with a note (use the target DB's native tooling), but uploads are still
archived.
"""
import shutil
import zipfile
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models.base import utcnow
from app.models.system import Backup


def _timestamp():
    return utcnow().strftime("%Y%m%d_%H%M%S")


def _sqlite_path():
    uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite:///"):
        return Path(uri.replace("sqlite:///", "", 1))
    return None


def create_backup(backup_type="Manual"):
    """Create a backup archive. Returns the Backup record."""
    backup_dir = Path(current_app.config["BACKUP_DIR"])
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = _timestamp()
    archive_path = backup_dir / f"backup_{backup_type.lower()}_{stamp}.zip"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        sqlite = _sqlite_path()
        if sqlite and sqlite.exists():
            zf.write(sqlite, arcname="cms.db")
        else:
            zf.writestr(
                "DATABASE_NOTE.txt",
                "Non-SQLite database detected. Use the database's native dump "
                "tool (e.g. pg_dump) for the data backup. Uploads are included.",
            )
        upload_dir = Path(current_app.config["UPLOAD_DIR"])
        if upload_dir.exists():
            for f in upload_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, arcname=str(Path("uploads") / f.relative_to(upload_dir)))

    record = Backup(
        backup_type=backup_type,
        file_path=str(archive_path),
        size_bytes=archive_path.stat().st_size,
        verified=verify_backup(archive_path),
    )
    db.session.add(record)
    db.session.commit()
    return record


def verify_backup(archive_path):
    """Return True if the zip is readable and not corrupt."""
    try:
        with zipfile.ZipFile(archive_path) as zf:
            return zf.testzip() is None
    except Exception:
        return False


def restore_backup(archive_path):
    """Restore the SQLite DB and uploads from a backup archive.
    Returns (ok, message). Existing DB is copied aside first."""
    archive = Path(archive_path)
    if not archive.exists():
        return False, "Backup file not found."
    if not verify_backup(archive):
        return False, "Backup archive is corrupt."

    sqlite = _sqlite_path()
    upload_dir = Path(current_app.config["UPLOAD_DIR"])

    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        if sqlite and "cms.db" in names:
            # Preserve current DB before overwriting
            if sqlite.exists():
                shutil.copy2(sqlite, sqlite.with_suffix(".db.pre_restore"))
            with zf.open("cms.db") as src, open(sqlite, "wb") as dst:
                shutil.copyfileobj(src, dst)
        for name in names:
            if name.startswith("uploads/"):
                target = upload_dir.parent / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    return True, "Restore complete. Restart the application to load restored data."
