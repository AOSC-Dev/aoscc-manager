from flask import Blueprint, render_template, redirect, url_for

from ..util.grant import revoke_client

bp = Blueprint('admin', __name__)


from . import grant, payment, notify, user, db, vote, draw, checkin, accommo


@bp.get('/')
def index():
    return render_template('admin/index.html')


@bp.get('/revoke')
def revoke():
    revoke_client()
    return redirect(url_for('admin.index'))
