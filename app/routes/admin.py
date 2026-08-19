from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.admin import RoleForm, UserForm
from app.models.system import AuditLog
from app.models.user import Permission, Role, RolePermission, User
from app.utils.decorators import require_permission

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@login_required
@require_permission("admin", "view")
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@require_permission("admin", "edit")
def user_create():
    form = UserForm()
    form.role_id.choices = _role_choices()
    if form.validate_on_submit():
        if not form.password.data:
            flash("Password is required for a new user.", "error")
            return render_template("admin/user_form.html", form=form, is_new=True)
        user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role_id.data,
            is_active=form.is_active.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, is_new=True)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("admin", "edit")
def user_edit(user_id):
    user = db.get_or_404(User, user_id)
    form = UserForm(obj=user)
    form.role_id.choices = _role_choices()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role_id.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, is_new=False, user=user)


@admin_bp.route("/roles")
@login_required
@require_permission("admin", "view")
def roles():
    all_roles = Role.query.order_by(Role.name).all()
    return render_template("admin/roles.html", roles=all_roles)


@admin_bp.route("/roles/<int:role_id>/permissions", methods=["GET", "POST"])
@login_required
@require_permission("admin", "edit")
def role_permissions(role_id):
    role = db.get_or_404(Role, role_id)
    permissions = Permission.query.order_by(
        Permission.module, Permission.action
    ).all()

    if request.method == "POST":
        selected = set(request.form.getlist("permission_ids", type=int))
        existing = {rp.permission_id: rp for rp in role.role_permissions}

        for pid in selected - set(existing):
            db.session.add(RolePermission(role_id=role.id, permission_id=pid))
        for pid in set(existing) - selected:
            db.session.delete(existing[pid])

        db.session.commit()
        flash(f"Permissions updated for {role.name}.", "success")
        return redirect(url_for("admin.role_permissions", role_id=role.id))

    granted = {rp.permission_id for rp in role.role_permissions}
    # Group permissions by module for the UI
    grouped = {}
    for perm in permissions:
        grouped.setdefault(perm.module, []).append(perm)

    return render_template(
        "admin/role_permissions.html",
        role=role,
        grouped=grouped,
        granted=granted,
    )


@admin_bp.route("/audit")
@login_required
@require_permission("admin", "view")
def audit_log():
    page = request.args.get("page", 1, type=int)
    logs = (
        AuditLog.query.order_by(AuditLog.action_date.desc())
        .paginate(page=page, per_page=50, error_out=False)
    )
    return render_template("admin/audit.html", logs=logs)


def _role_choices():
    return [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
