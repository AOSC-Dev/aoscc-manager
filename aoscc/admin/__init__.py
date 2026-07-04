import functools

from flask import Blueprint, redirect, url_for, g, flash

bp = Blueprint('admin', __name__)


@bp.before_request
def user_check():
    if not g.roles:
        return redirect(url_for('user.index'))


def has_role(role: str) -> bool:
    if 'admin' in g.roles:
        return True
    if role == '*':
        return bool(g.roles)
    return role in g.roles


@bp.app_context_processor
def inject_has_role():
    return dict(has_role=has_role)


def check_role(*roles):
    def wrapper(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if not any(has_role(role) for role in roles):
                flash('角色权限不足。')
                return redirect(url_for('admin.index'))
            return view(*args, **kwargs)
        return wrapped
    return wrapper


from . import index, notify, user, db, vote, draw, checkin
