import re
from time import time
from datetime import date, timedelta

from flask import render_template, flash, g, redirect, url_for, session

from ..config import *
from ..util.db import insert_dict, count_rows, query_all, delete_from, update_table
from ..util.tg import send_telegram
from ..util.form import Field, validate
from ..util.crypt import encrypt
from . import bp, nick_required, registered_only, badge, volunteer


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


def get_confirmed_count() -> int:
    return query_all('SELECT COUNT(*) AS cnt FROM register WHERE confirmed > 0')[0]['cnt']


def check_block_register() -> str:
    total = count_rows('register')
    not_confirmed = count_rows('register', {'confirmed': 0})
    confirmed = total - not_confirmed
    if g.registered:
        return '您已完成注册，请勿重复注册'
    if 'REGOK' in g.user['remarks']:
        return ''
    if not REGISTER_OPEN or NOW() >= REGISTER_CUTOFF:
        return '不在注册开放时间'
    if get_confirmed_count() >= REGISTER_CAP:
        return '注册人数已达上限'
    if NOW() < RESERVE_CUTOFF and count_rows('register') >= REGISTER_CAP:
        return '注册人数已达上限'
    return ''


@bp.post('/register')
@nick_required
def post_register():
    if msg := check_block_register():
        flash(f'当前{msg}！')
    elif form := validate(
        Field('真实姓名', 'legal_name', 1, 20, str, True),
        Field('公民身份号码', 'citizen_id', 18, 18, lambda x: str(x).upper(), check_citizen_id),
        Field('手机号码', 'phone', 11, 11, str, r'1[0-9]{10}'),
        Field('行程状态', 'confirmed', 1, 1, int, (0,1)),
        Field('必须阅知参会须知！', 'consent', 2, 2, str, 'on'),
    ):
        to_be_encrypted = f"{form['legal_name']}:{form['citizen_id']}:{form['phone']}"
        insert_dict('register', {
            'uid': g.uid,
            'legal_id': encrypt(to_be_encrypted),
            'confirmed': int(time()) if form['confirmed'] else 0,
        })
        flash('注册成功！')
        return redirect(url_for('user.index'))
    return redirect(url_for('user.register'))


@bp.post('/register/confirm')
@registered_only
def post_register_confirm():
    if get_confirmed_count() >= REGISTER_CAP:
        flash('注册人数已达上限，无法确认行程！')
    else:
        update_table('register', {'confirmed': int(time())}, {'uid': g.uid})
        flash('行程确认成功！')
    return redirect(url_for('user.index'))


@bp.post('/register/cancel')
@registered_only
def post_cancel():
    if g.arrived:
        flash('您已完成签到，无法取消注册！')
    elif g.confirmed:
        flash('您已确认行程，已通知会务组取消注册，我们将稍后与您联系。')
        send_telegram(REPORTING_ID, f'#REGISTER\n与会者 {g.uid} 申请取消注册，请及时处理')
    elif volunteer.is_volunteer():
        flash('您是已确认的志愿者，无法取消注册！请先联系会务组取消志愿者状态。')
    else:
        badge.post_badge_del()  # need to delete PNG file
        delete_from('register', {'uid': g.uid})  # most tables will CASCADE delete
        session.pop('_flashes', None)  # clear repetitive msg
        flash('取消成功！')
        return redirect(url_for('user.register'))
    return redirect(url_for('user.index'))


@bp.get('/register')
@nick_required
def register():
    if g.registered:
        return redirect(url_for('user.index'))
    return render_template('user/register.html', block_register=check_block_register())
