from flask import Blueprint, g, request, redirect, url_for

from ..util.db import fetch_one

bp = Blueprint('user', __name__)


@bp.before_request
def user_check():
    if not g.uid:  # all pages require logged in
        return redirect(url_for('login.login'))
    register = fetch_one('register', {'uid': g.uid})
    g.registered = bool(register)
    g.arrived = bool(register and register['arrived'])
    if not g.nick and request.endpoint not in ('user.info', 'user.post_info'):
        return redirect(url_for('user.info'))  # provide nick before other service


from . import info, register, merch, billing
