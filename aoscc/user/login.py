
from flask import render_template, redirect, url_for, flash, g, session, request

from ..config import *
from ..util.db import fetch_one, insert_dict, update_table
from ..util.tg import is_contributor_telegram
from ..util.form import Field, validate
from ..util.mail import send_email_login, is_contributor_email
from ..util.crypt import verify_msg
from . import bp


@bp.post('/login')
def post_login():
    if form := validate(
        Field('邮箱', 'email', 1, 254, str, r'(?i)[a-z0-9+_.-]+@[a-z0-9-]+(\.[a-z0-9-]+)+')
    ):
        if INTERNAL_ONLY and not is_contributor_email(form['email']):
            flash('封闭注册期，请使用指定的平台账号注册。')
            return redirect(url_for('user.login'))
        flash(send_email_login(form['email']))
    return redirect(url_for('user.login'))


@bp.get('/login/<string:token>')
def do_login(token: str):
    typ, iden = verify_msg(token)
    if typ not in ('telegram', 'email'):
        flash('无效登录凭据。')
        return redirect(url_for('user.login'))
    if 'bind' in request.args:
        typ_bind, uid = verify_msg(request.args['bind'])
        bind = int(uid) if typ_bind == 'bind' else 0
        if not bind:
            flash('无效绑定凭据。')
        elif not fetch_one('user', {'uid': bind}):
            flash('指定的账号不存在。')
        elif u := fetch_one('user', {typ: iden}):
            session['uid'] = u['uid']
            session.permanent = True
            flash('该 Telegram 账号或邮箱已被绑定，将进入该账号。')
        else:
            update_table('user', {typ: iden}, {'uid': bind})
            session['uid'] = bind
            session.permanent = True
            flash('绑定成功。')
        return redirect(url_for('user.info'))

    if row := fetch_one('user', {typ: iden}):
        session['uid'] = row['uid']
    else:
        if INTERNAL_ONLY and (
            (typ == 'telegram' and not is_contributor_telegram(int(iden))) or
            (typ == 'email' and not is_contributor_email(iden))
        ):
            flash('封闭注册期，请使用指定的平台账号注册。')
            return redirect(url_for('user.login'))
        session['uid'] = insert_dict('user', {typ: iden})
    session.permanent = True
    if ret := session.pop('login_return', None):
        return redirect(ret)
    return redirect(url_for('user.index'))


@bp.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


@bp.get('/login')
def login():
    if g.uid:
        return redirect(url_for('user.index'))
    return render_template('user/login.html')
