"""Authorization decorators."""
from functools import wraps

from flask import abort
from flask_login import current_user


def require_permission(module, action="view"):
    """Guard a view: the current user's role must grant module.action.
    Super Administrator bypasses all checks."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if _is_super_admin(current_user):
                return view(*args, **kwargs)
            if not current_user.has_permission(module, action):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def _is_super_admin(user):
    return bool(user.role and user.role.name == "Super Administrator")
