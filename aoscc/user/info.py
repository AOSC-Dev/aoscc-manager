from flask import render_template, flash, g, redirect, url_for

from ..config import *
from ..util.db import fetch_one, insert_dict
from ..util.form import Field, validate
from . import bp


@bp.post('/')
def post_info():
    if form := validate(
        Field('昵称', 'nick', 1, 50, str, True),
        Field('Telegram', 'telegram', 0, 35, str, True),
        Field('邮箱', 'email', 0, 254, str, True),
        Field('手机', 'phone', 0, 30, str, True),
        Field('QQ', 'qq', 0, 15, str, True),
        Field('微信', 'wechat', 0, 30, str, True),
    ):
        g.db.execute(
            'UPDATE user SET nick = ? WHERE uid = ?',
            (form.pop('nick'), g.uid),
        )
        g.db.commit()
        insert_dict('info', form|{'uid': g.uid})
        flash('保存成功！')
        return redirect(url_for('.register'))
    else:
        return redirect(url_for('.info'))


@bp.get('/')
def info():
    form = fetch_one('info', {'uid': g.uid})
    return render_template('info.html', form=form)
