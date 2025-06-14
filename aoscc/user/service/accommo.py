import math
import secrets
import functools

from flask import render_template, flash, g, redirect, url_for, session

from ...config import *
from ...util.db import query_all, fetch_all, fetch_one, insert_dict, delete_from
from ...util.form import Field, validate, parse_date
from . import bp


def is_accommo_open() -> bool:
    return NOW() < ACCOMMO_CLOSE


def accommo_open(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not is_accommo_open():
            flash('当前不在预订时间！')
            return redirect(url_for('.acccmmo'))
        return view(*args, **kwargs)
    return wrapped


def is_booked():
    bool(fetch_one('accommo', {'uid': g.uid}))


def _get_vacancy() -> dict[str, dict[str, int]]:
    try:
        v = {name: {'': room.vacancy} for name, room in ROOM_OFFERING.items()}
        res = query_all('SELECT room, type, COUNT(*) AS cnt FROM accommo GROUP BY room, type')
        for line in res:
            room = ROOM_OFFERING[line['room']]
            occupied_slots = line['cnt']
            allocated_rooms = math.ceil(occupied_slots / room.nguest)
            allocated_slots = allocated_rooms * room.nguest
            available_slots = allocated_slots - occupied_slots
            v[room.name][''] -= allocated_rooms
            if available_slots and not line['type'].startswith('单独入住'):
                v[room.name][line['type']] = available_slots
        return v
    except Exception as exc:
        print(exc)
        return {}


def _vacancy_str(room: dict[str, int]) -> str:
    if room[''] > 0:
        return f'余 {room[""]} 间'
    if len(room) == 1:
        return '已订完'
    ret = ['已无空房']
    if '男士随机' in room:
        ret.append(f'男士拼房余 {room["男士随机"]} 位')
    if '女士随机' in room:
        ret.append(f'女士拼房余 {room["女士随机"]} 位')
    if any(k not in ('', '男士随机', '女士随机') for k in room.keys()):
        ret.append('部分指定室友待拼')
    return '，'.join(ret)


def get_ngroupmate(room: str, type: str) -> int:
    return len(fetch_all('accommo', {'room': room, 'type': type}))


@bp.post('/accommo')
@accommo_open
def post_accommo():
    try:
        form = validate(
            Field('入住房型', 'room', 1, 10, str, lambda x: x in ROOM_OFFERING),
            Field('入住日期', 'checkin', 10, 10, str, True),
            Field('退房日期', 'checkout', 10, 10, str, True),
            Field('入住方式组别', 'type', 1, 20, str, True),
            Field('手机号', 'phone', 11, 11, str, r'1\d{10}'),
            Field('备注', 'other', 0, 500, str, True),
            Field('必须同意预订条款！', 'consent', 2, 2, str, 'on'),
        )
        form.pop('consent')
        checkin, checkout = map(parse_date, (form['checkin'], form['checkout']))
        if not (DATE_RANGE[0] <= checkin <= DATE_RANGE[1]):
            flash('入住日期不合法！')
        if not (DATE_RANGE[0]+ONE_DAY <= checkout <= DATE_RANGE[1]+ONE_DAY):
            flash('退房日期不合法！')
        if checkin >= checkout:
            flash('退房日期必须晚于入住日期！')
        if session.get("_flashes"):
            raise ValueError
    except Exception:
        return redirect(url_for('.accommo'))

    try:
        g.db.execute('BEGIN EXCLUSIVE')
        room = _get_vacancy()[form['room']]
        print(room)
        if not ((room[''] > 0) or (room.get(form['type'], 0) > 0)):
            raise ValueError
        price = ROOM_OFFERING[form['room']].price*(checkout-checkin).days
        if not form['type'].startswith('单独入住'):
            price /= 2
        bid = insert_dict('billing', {
            'uid': g.uid,
            'category': '住宿',
            'item': f'协议酒店住宿：{checkin.day}-{checkout.day}日',
            'spec': f'{form["room"]}-{form["type"]}',
            'quantity': 1,
            'price': price,
        })
        insert_dict('accommo', form|{'bid': bid, 'uid': g.uid})
        flash('预订成功！房间已为您预留，请前往支付。')
    except Exception:
        flash('预订失败！所选的房型和入住方式已订满。')
    finally:
        g.db.commit()

    return redirect(url_for('.accommo'))


@bp.post('/accommo/cancel')
@accommo_open
def post_accommo_cancel():
    delete_from('billing', {'uid': g.uid, 'category': '住宿'})
    # will CASCADE accommo
    flash('取消成功！')
    return redirect(url_for('.accommo'))


@bp.get('/accommo')
def accommo():
    form = fetch_one('accommo', {'uid': g.uid})
    if form:
        return render_template(
            'accommo.html', form=form,
            get_ngroupmate=get_ngroupmate,
        )
    else:
        return render_template(
            'accommo.html', form=form,
            vacancy=_get_vacancy(),
            vacancy_str=_vacancy_str,
            random_token=secrets.token_hex(3).upper(),
        )
