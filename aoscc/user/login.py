
from flask import Blueprint, render_template, redirect, url_for, flash, g

from ..config import *
from ..util.db import fetch_one, insert_dict
from ..util.form import Field, validate
from ..util.mail import send_email_login
from ..util.grant import update_grant
from ..util.verify import verify_msg

bp = Blueprint('login', __name__)


@bp.get('/login')
def login():
    return render_template('login.html')


@bp.post('/login')
def post_login():
    if form := validate(
        Field('邮箱', 'email', 1, 254, str, r'(?i)[a-z0-9+_.-]+@[a-z0-9-]+(\.[a-z0-9-]+)+')
    ):
        flash(send_email_login(form['email']))
    return redirect(url_for('.login'))


@bp.get('/login/<string:token>')
def do_login(token: str):
    typ, iden = verify_msg(token)
    if typ in ('telegram', 'email'):
        d = {'type': typ, 'identity': iden}
        if row := fetch_one('user', d):
            g.uid = row['uid']
        else:
            g.uid = insert_dict('user', d)
        update_grant()
        return redirect(url_for('user.register'))
    else:
        flash('无效登录凭据。')
        return redirect(url_for('.login'))



@bp.get('/logout')
def logout():
    g.uid = None
    update_grant()
    if g.roles:
        return redirect(url_for('admin.index'))
    else:
        return redirect(url_for('.login'))
