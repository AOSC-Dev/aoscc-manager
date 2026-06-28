from time import time

from flask import redirect, url_for, session, flash, request

from ..config import *
from ..util.db import update_table
from ..util.form import Field, validate
from ..util.crypt import verify_msg
from . import bp, check_role


@bp.post('/checkin/<int:uid>')
@check_role('checkin')
def post_user_checkin(uid: int):
    if form := validate(
        Field('操作', 'action', 1, 10, str, ('checkin', 'cancel')),
    ):
        t = int(time()) if (form['action'] == 'checkin') else 0
        update_table('register', {'arrived': t}, {'uid': uid})
    return redirect(url_for('admin.user', uid=uid))


@bp.get('/checkin/<string:token>')
@bp.post('/checkin', defaults={'token': None})
@check_role('checkin')  # see below
def post_checkin(token: str):
    token = request.form.get('token', token)
    try:
        if not isinstance(token, str):
            raise AssertionError
        else:
            token = token.removeprefix(URL_BASE+url_for('admin.post_checkin')+'/')
            typ, msg = verify_msg(token)
            if typ != 'checkin':
                raise AssertionError
            session['_last_checkin_token'] = token
            return redirect(url_for('admin.user', uid=int(msg)))
    except AssertionError:
        flash('无效签到码！')
        return redirect(url_for('admin.user'))
