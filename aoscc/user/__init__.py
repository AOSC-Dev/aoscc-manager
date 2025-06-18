from flask import Blueprint, g, request, redirect, url_for

from ..util.db import fetch_one

bp = Blueprint('user', __name__, template_folder='templates')

from . import info, register, merch, billing


@bp.before_request
def acl_check():
    if request.blueprint == 'user.login':  # do not regulate login/logout
        return
    if not g.uid:  # all pages require logged in
        return redirect(url_for('user.login.login'))
    register = fetch_one('register', {'uid': g.uid})
    g.registered = bool(register)
    g.arrived = bool(register) and bool(register['arrived'])
    if not g.nick and request.path != '/':  # provide nick before other service
        return redirect(url_for('user.info'))


from .login import bp as login_bp
from .service import bp as service_bp

bp.register_blueprint(login_bp)
bp.register_blueprint(service_bp)
