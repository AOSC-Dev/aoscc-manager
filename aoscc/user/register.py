import re
from datetime import date, timedelta

from flask import render_template, flash, g, redirect, url_for

from ..config import *
from ..util.db import fetch_one, insert_dict
from ..util.form import Field, validate
from ..util.encrypt import encrypt
from . import bp


def is_registered() -> bool:
    return bool(fetch_one('register', {'uid': g.uid}))


def check_citizen_id(id: str) -> bool:
    if not re.fullmatch(r'([1-6]\d{5}|(8[1-3])0000)\d{11}[0-9X]', id):
        return False  # overall format and coarse district code check
    try:  # date validity
        dob = date(int(id[6:10]), int(id[10:12]), int(id[12:14]))
        today = date.today()
        if dob > today or dob - today > timedelta(days=365*150):
            return False  # no deceased id ...
    except Exception:
        return False
    a = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    c = sum([int(id[i]) * a[i] for i in range(17)]) % 11
    p = ['1','0','X','9','8','7','6','5','4','3','2']
    return id[17] == p[c]  # parity digit check


@bp.post('/register')
def post_register():
    if is_registered():  # no slience update, use cancellation
        flash('信息已存在！')
    elif form := validate(
        Field('真实姓名', 'legal_name', 1, 20, str, True),
        Field('身份证号', 'citizen_id', 18, 18, lambda x: str(x).upper(), check_citizen_id),
        Field('必须阅知参会须知！', 'consent', 2, 2, str, 'on'),
    ):
        insert_dict('register', {
            'uid': g.uid,
            'legal_id': encrypt(f'{form['legal_name']}:{form['citizen_id']}')
        })
        flash('注册成功！')
        return redirect(url_for('.service.index'))
    return redirect(url_for('.register'))


@bp.get('/register')
def register():
    if is_registered():
        return redirect(url_for('.service.index'))
    return render_template('register.html')
