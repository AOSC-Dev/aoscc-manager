from flask import render_template, g, url_for, redirect, flash

from ..config import *
from ..util.db import query_all, fetch_one
from ..util.form import Field, validate
from ..util.grant import update_grant
from . import bp, check_role


@bp.post('/user/login')
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
    return redirect(url_for('.user'))


@bp.get('/user')
@check_role('admin')
def user():
    users = query_all('SELECT * FROM user JOIN info USING(uid)')
    return render_template('user.html', users=users)
