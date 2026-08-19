"""Application factory."""
from flask import Flask

from app.config import get_config
from app.extensions import bcrypt, csrf, db, login_manager, mail, migrate


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    _init_extensions(app)
    _ensure_data_dirs(app)
    _register_blueprints(app)
    _register_security(app)
    _register_shell(app)
    _register_template_helpers(app)

    from app.utils.audit import init_audit

    init_audit(app)
    _register_cli(app)

    from app.utils.scheduler import init_scheduler

    init_scheduler(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


def _ensure_data_dirs(app):
    app.config["UPLOAD_DIR"].mkdir(parents=True, exist_ok=True)
    app.config["BACKUP_DIR"].mkdir(parents=True, exist_ok=True)


def _register_blueprints(app):
    # Blueprints are added phase by phase. Import guarded so the app runs
    # even before later-phase modules exist.
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)

    _try_register(app, "app.routes.auth", "auth_bp")
    _try_register(app, "app.routes.admin", "admin_bp")
    _try_register(app, "app.routes.members", "members_bp")
    _try_register(app, "app.routes.family", "family_bp")
    _try_register(app, "app.routes.church", "church_bp")
    _try_register(app, "app.routes.events", "events_bp")
    _try_register(app, "app.routes.attendance", "attendance_bp")
    _try_register(app, "app.routes.outreach", "outreach_bp")
    _try_register(app, "app.routes.pastoral", "pastoral_bp")
    _try_register(app, "app.routes.friday_school", "friday_school_bp")
    _try_register(app, "app.routes.finance", "finance_bp")
    _try_register(app, "app.routes.inventory", "inventory_bp")
    _try_register(app, "app.routes.communication", "communication_bp")
    _try_register(app, "app.routes.reports", "reports_bp")
    _try_register(app, "app.routes.backup", "backup_bp")
    _try_register(app, "app.routes.api", "api_bp")


def _try_register(app, module_path, bp_name):
    import importlib

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return
    bp = getattr(module, bp_name, None)
    if bp is not None and bp_name not in {b.name for b in app.blueprints.values()}:
        app.register_blueprint(bp)


def _register_security(app):
    from datetime import datetime, timedelta

    from flask import flash, redirect, session, url_for
    from flask_login import current_user, logout_user

    from app.models.base import utcnow

    @app.before_request
    def enforce_session_timeout():
        if not current_user.is_authenticated:
            return
        timeout = timedelta(minutes=app.config["SESSION_TIMEOUT_MINUTES"])
        now = utcnow()
        last = session.get("last_activity")
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
            except (TypeError, ValueError):
                last_dt = now
            if now - last_dt > timeout:
                logout_user()
                session.clear()
                flash("Session expired due to inactivity. Please log in again.", "warning")
                return redirect(url_for("auth.login"))
        session["last_activity"] = now.isoformat()

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        )
        return response


def _register_template_helpers(app):
    @app.template_global()
    def endpoint_exists(endpoint):
        return endpoint in app.view_functions


def _register_cli(app):
    import click

    @app.cli.command("init-rbac")
    def init_rbac():
        """Seed roles, permissions, and the role-permission matrix."""
        from app.utils.rbac_seed import seed_rbac

        seed_rbac()
        click.echo("RBAC seeded (roles, permissions, grants).")

    @app.cli.command("create-admin")
    @click.option("--username", default="admin", prompt=True)
    @click.option("--email", default="admin@example.com", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, email, password):
        """Create a Super Administrator user."""
        from app.utils.rbac_seed import create_superadmin, seed_rbac

        seed_rbac()
        user, created = create_superadmin(username, email, password)
        click.echo(
            f"Super admin '{user.username}' "
            + ("created." if created else "already exists.")
        )


def _register_shell(app):
    @app.shell_context_processor
    def shell_context():
        import app.models as models

        return {"db": db, **{n: getattr(models, n) for n in dir(models) if n[0].isupper()}}
