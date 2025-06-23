from flask import Blueprint, g, request, redirect, url_for

from ..util.db import fetch_one

bp = Blueprint('user', __name__)


@bp.before_request
def user_check():
    if not g.uid:  # all pages require logged in
        return redirect(url_for('login.login'))
    g.register = fetch_one('register', {'uid': g.uid})
    g.registered = bool(g.register and (g.register['arrived'] >= 0))
    g.arrived = (g.register['arrived'] > 0) if g.register else False
    if not g.nick and request.endpoint not in ('user.info', 'user.post_info'):
        return redirect(url_for('user.info'))  # provide nick before other service


from . import info, register, merch, billing
