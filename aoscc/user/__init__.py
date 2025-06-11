from flask import Blueprint, g, request, redirect, url_for

bp = Blueprint('user', __name__, template_folder='templates')

from . import info, register, merch, billing


@bp.before_request
def acl_check():
    if request.blueprint == 'user.login':  # do not regulate login/logout
        return
    if not g.uid:  # all pages require logged in
        return redirect(url_for('user.login.login'))
    if not g.nick and request.path != '/':  # provide nick before other service
        return redirect(url_for('user.info'))


@bp.context_processor
def check_registered():
    return dict(registered=register.is_registered())


from .login import bp as login_bp
from .service import bp as service_bp

bp.register_blueprint(login_bp)
bp.register_blueprint(service_bp)
