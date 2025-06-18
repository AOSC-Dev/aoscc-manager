from flask import render_template, flash, redirect, url_for, g

from ..config import *
from ..util.db import query_all, fetch_one
from ..util.form import Field, validate
from ..util.grant import check_role, add_role, revoke_client, update_grant
from . import bp


@bp.post('/grant')
@check_role('admin')
def post_grant():
    if form := validate(
        Field('客户端 ID', 'id', 32, 32, str, r'[0-9a-f]{32}'),
        Field('授予角色', 'role', 0, 20, str, r'[a-z]+'),
    ):
        if not form['role']:
            revoke_client(form['id'])
            flash('撤销成功！')
        else:
            add_role(form['id'], form['role'])
            flash('授权成功！')
    return redirect(url_for('.grant'))


@bp.post('/grant/login')
@check_role('admin')
def post_user_login():
    if form := validate(
        Field('用户 ID', 'uid', 1, 10, int, lambda x: x>0),
    ):
        if fetch_one('user', {'uid': form['uid']}):
            g.uid = form['uid']
            update_grant()
            return redirect(url_for('user.register'))
        else:
            flash('用户不存在！')        
    return redirect(url_for('.grant'))


@bp.get('/grant')
@check_role('admin')
def grant():
    admins = query_all('SELECT id,roles FROM grant WHERE roles != ""')
    return render_template('grant.html', admins=admins)
