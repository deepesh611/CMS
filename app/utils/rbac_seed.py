"""Seed roles, permissions, and the role-permission matrix.

Idempotent: safe to run multiple times. Used by the `flask init-rbac` CLI
command and by seed_data.py.
"""
from app.extensions import db
from app.models.user import Permission, Role, RolePermission

# Modules that support permission control, with the actions each exposes.
MODULES = {
    "members": ["view", "edit", "delete"],
    "family": ["view", "edit", "delete"],
    "ministries": ["view", "edit", "delete"],
    "care_cells": ["view", "edit", "delete"],
    "events": ["view", "edit", "delete"],
    "attendance": ["view", "edit"],
    "outreach": ["view", "edit", "delete"],
    "visitors": ["view", "edit", "delete"],
    "friday_school": ["view", "edit", "delete"],
    "counselling": ["view", "edit", "delete"],
    "prayer": ["view", "edit", "delete"],
    "welfare": ["view", "edit", "approve"],
    "finance": ["view", "edit", "delete"],
    "inventory": ["view", "edit", "delete"],
    "communication": ["view", "edit", "send"],
    "reports": ["view", "export"],
    "admin": ["view", "edit"],
    "backup": ["view", "edit"],
}

# The 16 roles from the spec.
ROLES = [
    ("Super Administrator", "Full unrestricted access"),
    ("IT Administrator", "System, RBAC and configuration"),
    ("Church Administrator", "Day-to-day church operations"),
    ("Senior Pastor", "Pastoral oversight"),
    ("Associate Pastor", "Pastoral duties"),
    ("Elder", "Leadership oversight"),
    ("Secretary", "Records and correspondence"),
    ("Finance Officer", "Financial management"),
    ("Ministry Leader", "Ministry management"),
    ("Care Cell Leader", "Care cell management"),
    ("Counsellor", "Counselling cases"),
    ("Outreach Leader", "Outreach and visitors"),
    ("Friday School Coordinator", "Friday school oversight"),
    ("Friday School Teacher", "Class attendance and performance"),
    ("Communications Officer", "Messaging and announcements"),
    ("Read Only User", "View-only access"),
]

# Default permission grants per role. "*" = every permission.
# A module name grants all actions for that module.
# A "module.action" string grants just that action.
ROLE_GRANTS = {
    "Super Administrator": "*",
    "IT Administrator": "*",
    "Church Administrator": [
        "members", "family", "ministries", "care_cells", "events",
        "attendance", "outreach", "visitors", "friday_school",
        "communication", "reports",
    ],
    "Senior Pastor": [
        "members", "family", "ministries", "care_cells", "events",
        "attendance", "counselling", "prayer", "welfare", "reports",
    ],
    "Associate Pastor": [
        "members.view", "family.view", "events", "attendance",
        "counselling", "prayer", "reports.view",
    ],
    "Elder": [
        "members.view", "ministries.view", "care_cells", "events.view",
        "attendance", "reports.view",
    ],
    "Secretary": [
        "members", "family", "events", "attendance", "communication",
        "reports.view",
    ],
    "Finance Officer": ["finance", "welfare", "reports"],
    "Ministry Leader": ["ministries", "members.view", "attendance", "reports.view"],
    "Care Cell Leader": ["care_cells", "members.view", "attendance", "reports.view"],
    "Counsellor": ["counselling", "prayer", "members.view"],
    "Outreach Leader": ["outreach", "visitors", "members.view", "reports.view"],
    "Friday School Coordinator": ["friday_school", "reports.view"],
    "Friday School Teacher": [
        "friday_school.view", "friday_school.edit",
    ],
    "Communications Officer": ["communication", "members.view", "reports.view"],
    "Read Only User": [f"{m}.view" for m in MODULES if "view" in MODULES[m]],
}


def seed_permissions():
    existing = {(p.module, p.action) for p in Permission.query.all()}
    for module, actions in MODULES.items():
        for action in actions:
            if (module, action) not in existing:
                db.session.add(
                    Permission(
                        name=f"{module}.{action}",
                        module=module,
                        action=action,
                    )
                )
    db.session.commit()


def seed_roles():
    existing = {r.name for r in Role.query.all()}
    for name, desc in ROLES:
        if name not in existing:
            db.session.add(Role(name=name, description=desc))
    db.session.commit()


def _resolve_grants(grant_spec):
    """Expand a grant spec into a set of (module, action) tuples."""
    if grant_spec == "*":
        return {(m, a) for m, actions in MODULES.items() for a in actions}
    resolved = set()
    for item in grant_spec:
        if "." in item:
            module, action = item.split(".", 1)
            if module in MODULES and action in MODULES[module]:
                resolved.add((module, action))
        elif item in MODULES:
            for action in MODULES[item]:
                resolved.add((item, action))
    return resolved


def seed_role_permissions():
    perm_lookup = {(p.module, p.action): p.id for p in Permission.query.all()}
    for role in Role.query.all():
        grant_spec = ROLE_GRANTS.get(role.name, [])
        wanted = _resolve_grants(grant_spec)
        current = {rp.permission_id for rp in role.role_permissions}
        for module, action in wanted:
            pid = perm_lookup.get((module, action))
            if pid and pid not in current:
                db.session.add(RolePermission(role_id=role.id, permission_id=pid))
    db.session.commit()


def seed_rbac():
    seed_permissions()
    seed_roles()
    seed_role_permissions()


def create_superadmin(username, email, password):
    from app.models.user import User

    role = Role.query.filter_by(name="Super Administrator").first()
    user = User.query.filter_by(username=username).first()
    if user:
        return user, False
    user = User(username=username, email=email, role_id=role.id if role else None)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, True
