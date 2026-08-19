"""Users, roles, permissions, and the role-permission matrix."""
from flask_login import UserMixin

from app.extensions import bcrypt, db
from app.models.base import TimestampMixin, utcnow


class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column("RoleID", db.Integer, primary_key=True)
    name = db.Column("RoleName", db.String(80), unique=True, nullable=False)
    description = db.Column("Description", db.String(255))

    users = db.relationship("User", back_populates="role")
    role_permissions = db.relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def has_permission(self, module, action):
        for rp in self.role_permissions:
            perm = rp.permission
            if perm.module == module and perm.action == action:
                return True
        return False

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(TimestampMixin, db.Model):
    __tablename__ = "permissions"

    id = db.Column("PermissionID", db.Integer, primary_key=True)
    name = db.Column("PermissionName", db.String(120), nullable=False)
    module = db.Column("ModuleName", db.String(80), nullable=False, index=True)
    action = db.Column("Action", db.String(40), nullable=False, default="view")

    __table_args__ = (
        db.UniqueConstraint("ModuleName", "Action", name="uq_permission_module_action"),
    )

    role_permissions = db.relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Permission {self.module}.{self.action}>"


class RolePermission(TimestampMixin, db.Model):
    __tablename__ = "role_permissions"

    id = db.Column("RolePermissionID", db.Integer, primary_key=True)
    role_id = db.Column("RoleID", db.Integer, db.ForeignKey("roles.RoleID"), nullable=False)
    permission_id = db.Column(
        "PermissionID", db.Integer, db.ForeignKey("permissions.PermissionID"), nullable=False
    )

    role = db.relationship("Role", back_populates="role_permissions")
    permission = db.relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        db.UniqueConstraint("RoleID", "PermissionID", name="uq_role_permission"),
    )


class User(TimestampMixin, UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column("UserID", db.Integer, primary_key=True)
    username = db.Column("Username", db.String(80), unique=True, nullable=False)
    password_hash = db.Column("PasswordHash", db.String(255), nullable=False)
    email = db.Column("Email", db.String(120), unique=True, nullable=False)
    role_id = db.Column("RoleID", db.Integer, db.ForeignKey("roles.RoleID"))
    is_active = db.Column("IsActive", db.Boolean, default=True, nullable=False)

    # Link to a member record (optional — staff may not be members)
    member_id = db.Column("MemberID", db.Integer, db.ForeignKey("members.MemberID"))

    # 2FA
    totp_secret = db.Column("TotpSecret", db.String(64))
    twofa_enabled = db.Column("TwoFAEnabled", db.Boolean, default=False, nullable=False)

    # Account lockout
    failed_login_count = db.Column("FailedLoginCount", db.Integer, default=0, nullable=False)
    locked_until = db.Column("LockedUntil", db.DateTime)
    last_login_at = db.Column("LastLoginAt", db.DateTime)

    role = db.relationship("Role", back_populates="users")
    member = db.relationship("Member", foreign_keys=[member_id])

    # --- password helpers ----------------------------------------------
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # --- lockout helpers -----------------------------------------------
    @property
    def is_locked(self):
        return self.locked_until is not None and self.locked_until > utcnow()

    def get_id(self):
        return str(self.id)

    def has_permission(self, module, action):
        return bool(self.role and self.role.has_permission(module, action))

    def __repr__(self):
        return f"<User {self.username}>"
