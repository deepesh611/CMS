from app.models.system import AuditLog
from app.models.user import Permission, Role, RolePermission, User


def test_all_roles_seeded(app):
    with app.app_context():
        assert Role.query.count() == 16


def test_permissions_seeded(app):
    with app.app_context():
        assert Permission.query.count() > 0
        # finance module should expose view/edit/delete
        actions = {
            p.action for p in Permission.query.filter_by(module="finance").all()
        }
        assert {"view", "edit", "delete"} <= actions


def test_finance_officer_grants(app):
    with app.app_context():
        role = Role.query.filter_by(name="Finance Officer").first()
        assert role.has_permission("finance", "edit")
        assert not role.has_permission("members", "edit")


def test_read_only_user_is_view_only(app):
    with app.app_context():
        role = Role.query.filter_by(name="Read Only User").first()
        for rp in role.role_permissions:
            assert rp.permission.action == "view"


def test_super_admin_has_member_permission(app):
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        assert user.role.name == "Super Administrator"


def test_audit_log_records_insert(app, db):
    with app.app_context():
        role = Role.query.filter_by(name="Elder").first()
        perm = Permission.query.filter_by(module="finance", action="edit").first()
        db.session.add(RolePermission(role_id=role.id, permission_id=perm.id))
        db.session.commit()
        entry = (
            AuditLog.query.filter_by(table_name="role_permissions", action="INSERT")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert entry is not None
