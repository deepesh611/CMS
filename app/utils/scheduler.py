"""In-process scheduled jobs (APScheduler): birthday/anniversary greetings
and automatic backups. No external broker required — suits single-server
Windows/Docker deployment."""
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(daemon=True)


def init_scheduler(app):
    if app.config.get("TESTING"):
        return
    # Avoid double-starting under the Flask reloader (child process only).
    import os

    if app.config.get("DEBUG") and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return
    if scheduler.running:
        return

    scheduler.add_job(
        lambda: run_birthday_greetings(app),
        "cron",
        hour=7,
        id="birthday_greetings",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: run_auto_backup(app, "Daily"),
        "cron",
        hour=2,
        id="daily_backup",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: run_auto_backup(app, "Weekly"),
        "cron",
        day_of_week="sun",
        hour=3,
        id="weekly_backup",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: run_auto_backup(app, "Monthly"),
        "cron",
        day=1,
        hour=4,
        id="monthly_backup",
        replace_existing=True,
    )
    scheduler.start()


def run_birthday_greetings(app):
    with app.app_context():
        from app.extensions import db
        from app.models.communication import Communication, EmailLog
        from app.models.member import Member
        from app.utils.communication import send_email

        today = date.today()
        members = Member.query.filter(Member.dob.isnot(None)).all()
        celebrants = [
            m for m in members
            if m.dob and m.dob.month == today.month and m.dob.day == today.day
        ]
        if not celebrants:
            return

        for m in celebrants:
            if not m.email:
                continue
            comm = Communication(
                channel="Email",
                category="Birthday",
                subject="Happy Birthday!",
                body=f"Dear {m.first_name}, the church family wishes you a "
                     f"blessed and joyful birthday!",
                status="Sent",
            )
            db.session.add(comm)
            db.session.flush()
            ok, err = send_email(m.email, comm.subject, comm.body)
            db.session.add(
                EmailLog(
                    communication_id=comm.id,
                    recipient=m.email,
                    status="Sent" if ok else "Failed",
                    error=err,
                )
            )
        db.session.commit()


def run_auto_backup(app, backup_type):
    with app.app_context():
        from app.utils.backup import create_backup

        create_backup(backup_type=backup_type)
