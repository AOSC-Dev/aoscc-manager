from pathlib import Path

from flask import render_template, flash, redirect, url_for, session, g, send_file, current_app, abort

from ..config import *
from ..secret import BOT_TOKEN
from ..util.db import fetch_all, fetch_one, update_table
from ..util.form import Field, validate
from ..util.crypt import verify_msg
from . import bp, check_role, has_role


@bp.post('/user/<int:uid>')
@check_role('user')
def post_user_remarks(uid: int):
    if form := validate(
        Field('会务备注', 'remarks', 0, 500, str, True),
    ):
        update_table('user', {'remarks': form['remarks']}, {'uid': uid})
    return redirect(url_for('admin.user', uid=uid))


@bp.get('/user/<int:uid>/badge')
@check_role('user')
def user_badge(uid: int):
    return send_file(Path(current_app.instance_path) / 'badges' / f'{uid}.png', 'image/png')


@bp.get('/user/<int:uid>/telegram')
@check_role('admin')
def user_telegram_info(uid: int):
    if not (user := fetch_one('user', {'uid': uid})) or not user['telegram']:
        abort(404)
    return redirect(f'https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={user['telegram']}')


@bp.get('/user/<int:uid>')
@bp.get('/user', defaults={'uid': None})
@check_role('user')
def user(uid: int):
    if uid is not None:
        scanned = (('checkin', str(uid)) == verify_msg(session.get('_last_checkin_token')))
        if not (user := fetch_one('user', {'uid': uid})):
            flash('用户不存在！')
            return redirect(url_for('admin.user' if has_role('checkin') else 'admin.users'))
        register = fetch_one('register', {'uid': uid})
        volunteer = fetch_one('volunteer', {'uid': uid, 'status': 1})
        badge = fetch_one('badge', {'uid': uid})
    return render_template('admin/user.html', **locals())


@bp.post('/user/<int:uid>/login')
@check_role('admin')
def post_force_login(uid: int):
    if fetch_one('user', {'uid': uid}):
        session['uid'] = uid
        session.permanent = True
        return redirect(url_for('user.index'))
    else:
        flash('用户不存在！')        
        return redirect(url_for('admin.users'))


@bp.get('/list')
@check_role('*')
def users():
    users = fetch_all('user LEFT JOIN register USING(uid)')
    return render_template('admin/list.html', users=users)
