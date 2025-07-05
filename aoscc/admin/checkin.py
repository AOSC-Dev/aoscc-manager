from time import time

from flask import render_template, redirect, url_for, session, flash, request, g

from ..config import *
from ..util.db import update_table
from ..util.form import Field, validate
from ..util.grant import check_role, has_role
from ..util.verify import verify_msg
from . import bp


@bp.post('/checkin/<int:uid>/pickup/<int:bid>')
@bp.post('/checkin/<int:uid>/pickup/all', defaults={'bid': None})
@check_role('checkin')
def post_merch_pickup(uid: int, bid: int):
    g.db.execute(
        'UPDATE billing SET status = 2 WHERE category = "纪念品" AND status = 1'
        ' AND uid = ?' + (' AND bid = ?' if bid else ''),
        (uid,) + ((bid,) if bid else ())
    )
    g.db.commit()
    return redirect(url_for('admin.user', uid=uid))


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
#@check_role('checkin')  # see below
def post_checkin(token: str):
    if not has_role('checkin'):
        if token and request.method == 'GET':
            return render_template('admin/checkin-401.html')
        flash('角色权限不足。')
        return redirect(url_for('admin.index'))

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
