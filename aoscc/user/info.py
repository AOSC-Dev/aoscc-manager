from flask import render_template, flash, g, redirect, session, url_for

from ..config import *
from ..util.db import update_table, delete_from
from ..util.mail import send_email_login
from ..util.form import Field, validate
from ..util.crypt import sign_msg
from . import bp, login_required


@bp.post('/info/nick')
@login_required
def post_nick():
    if g.arrived:
        flash('您已签到，无法修改昵称。')
    elif form := validate(
        Field('昵称', 'nick', 1, 50, str, True),
    ):
        update_table('user', form, {'uid': g.uid})
        flash('保存成功！')
    return redirect(url_for('user.info'))


def _bind_token():
    return sign_msg('bind', g.uid, LOGIN_TOKEN_EXPIRY*60)


@bp.post('/info/telegram/bind')
@login_required
def bind_telegram():
    return redirect('https://t.me/AOSCCbot?start='+_bind_token().replace(':', '_'))


@bp.post('/info/email/bind')
@login_required
def bind_email():
    if form := validate(
        Field('邮箱', 'email', 1, 254, str, r'(?i)[a-z0-9+_.-]+@[a-z0-9-]+(\.[a-z0-9-]+)+')
    ):
        flash(send_email_login(form['email'], bind=_bind_token()))
    return redirect(url_for('user.info'))


@bp.post('/info/telegram/unbind')
@login_required
def unbind_telegram():
    if g.user['email'] is None:
        flash('解绑 Telegram 账号前请先绑定邮箱。')
    else:
        update_table('user', {'telegram': None}, {'uid': g.uid})
        flash('解绑成功！')
    return redirect(url_for('user.info'))


@bp.post('/info/email/unbind')
@login_required
def unbind_email():
    if g.user['telegram'] is None:
        flash('解绑邮箱前请先绑定 Telegram 账号。')
    else:
        update_table('user', {'email': None}, {'uid': g.uid})
        flash('解绑成功！')
    return redirect(url_for('user.info'))


@bp.post('/info/delete_account')
@login_required
def post_delete_account():
    if g.registered:
        flash('您已注册会议，请先取消注册再删除账号。')
        return redirect(url_for('user.register'))
    delete_from('user', {'uid': g.uid})
    flash('您的账号已删除。')
    session.clear()
    return redirect(url_for('user.login'))


@bp.get('/info')
@login_required
def info():
    return render_template('user/info.html')
