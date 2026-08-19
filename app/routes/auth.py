import base64
from datetime import timedelta
from io import BytesIO

import pyotp
import qrcode
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms.auth import (
    ChangePasswordForm,
    Enable2FAForm,
    LoginForm,
    TwoFactorForm,
)
from app.models.base import utcnow
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.is_locked:
            flash(
                "Account is temporarily locked due to failed login attempts. "
                "Try again later.",
                "error",
            )
            return render_template("auth/login.html", form=form)

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("This account is disabled. Contact an administrator.", "error")
                return render_template("auth/login.html", form=form)

            user.failed_login_count = 0
            user.locked_until = None
            db.session.commit()

            if user.twofa_enabled:
                session["pending_2fa_user"] = user.id
                return redirect(url_for("auth.two_factor"))

            _complete_login(user)
            return redirect(url_for("dashboard.index"))

        # Failed login → increment counter / lockout
        if user:
            _register_failed_attempt(user)
        flash("Invalid username or password.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/2fa", methods=["GET", "POST"])
def two_factor():
    user_id = session.get("pending_2fa_user")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, user_id)
    form = TwoFactorForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(form.token.data, valid_window=1):
            session.pop("pending_2fa_user", None)
            _complete_login(user)
            return redirect(url_for("dashboard.index"))
        flash("Invalid authentication code.", "error")

    return render_template("auth/two_factor.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/security", methods=["GET"])
@login_required
def setup_2fa():
    pw_form = ChangePasswordForm()
    enable_form = Enable2FAForm()
    qr_data = None

    if not current_user.twofa_enabled:
        if not current_user.totp_secret:
            current_user.totp_secret = pyotp.random_base32()
            db.session.commit()
        qr_data = _provisioning_qr(current_user)

    return render_template(
        "auth/security.html",
        pw_form=pw_form,
        enable_form=enable_form,
        qr_data=qr_data,
    )


@auth_bp.route("/2fa/enable", methods=["POST"])
@login_required
def enable_2fa():
    form = Enable2FAForm()
    if form.validate_on_submit():
        totp = pyotp.TOTP(current_user.totp_secret)
        if totp.verify(form.token.data, valid_window=1):
            current_user.twofa_enabled = True
            db.session.commit()
            flash("Two-factor authentication is now enabled.", "success")
        else:
            flash("Invalid code — 2FA not enabled.", "error")
    return redirect(url_for("auth.setup_2fa"))


@auth_bp.route("/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    current_user.twofa_enabled = False
    current_user.totp_secret = None
    db.session.commit()
    flash("Two-factor authentication disabled.", "warning")
    return redirect(url_for("auth.setup_2fa"))


@auth_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
        else:
            flash("Current password is incorrect.", "error")
    return redirect(url_for("auth.setup_2fa"))


# --- helpers -----------------------------------------------------------
def _complete_login(user):
    user.last_login_at = utcnow()
    db.session.commit()
    login_user(user)
    session["last_activity"] = utcnow().isoformat()


def _register_failed_attempt(user):
    user.failed_login_count = (user.failed_login_count or 0) + 1
    if user.failed_login_count >= current_app.config["MAX_LOGIN_ATTEMPTS"]:
        user.locked_until = utcnow() + timedelta(
            minutes=current_app.config["ACCOUNT_LOCKOUT_MINUTES"]
        )
        user.failed_login_count = 0
    db.session.commit()


def _provisioning_qr(user):
    uri = pyotp.TOTP(user.totp_secret).provisioning_uri(
        name=user.email, issuer_name="Church ERP"
    )
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
