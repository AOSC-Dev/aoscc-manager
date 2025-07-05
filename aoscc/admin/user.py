from pathlib import Path

from flask import render_template, flash, redirect, url_for, session, g, send_file, current_app

from ..config import *
from ..util.db import fetch_all, fetch_one, update_table
from ..util.form import Field, validate
from ..util.grant import check_role, has_role
from ..util.verify import verify_msg
from . import bp


@bp.post('/user/<int:uid>')
@check_role('*')
def post_user_remarks(uid: int):
    if form := validate(
        Field('会务备注', 'remarks', 0, 500, str, True),
    ):
        update_table('user', {'remarks': form['remarks']}, {'uid': uid})
    return redirect(url_for('admin.user', uid=uid))


@bp.get('/user/<int:uid>/badge')
@check_role('*')
def user_badge(uid: int):
    return send_file(Path(current_app.instance_path) / 'badges' / f'{uid}.png', 'image/png')


@bp.get('/user/<int:uid>')
@bp.get('/user', defaults={'uid': None})
@check_role('*')
def user(uid: int):
    if uid is not None:
        scanned = (('checkin', str(uid)) == verify_msg(session.get('_last_checkin_token')))
        if not (user := fetch_one('user', {'uid': uid})):
            flash('用户不存在！')
            return redirect(url_for('admin.user' if has_role('checkin') else 'admin.users'))
        info = fetch_one('info', {'uid': uid})
        register = fetch_one('register', {'uid': uid})
        volunteer = fetch_one('volunteer', {'uid': uid, 'status': 1})
        accommo = fetch_one('accommo', {'uid': uid})
        badge = fetch_one('badge', {'uid': uid})
        billing = fetch_all('billing', {'uid': uid})
        balance = fetch_one('unpaid_balance', {'uid': uid})['balance']
        merch    = list(filter(lambda x: x['category'] == '纪念品', billing))
        ready    = list(filter(lambda x: x['status'] == 1, merch))
        shipped  = list(filter(lambda x: x['status'] == 2, merch))
        notready = list(filter(lambda x: x['status'] == 0, merch))
    return render_template('admin/user.html', **locals())


@bp.get('/list')
@check_role('*')
def users():
    users = fetch_all('user LEFT JOIN info USING(uid) LEFT JOIN register USING(uid)')
    return render_template('admin/list.html', users=users)
