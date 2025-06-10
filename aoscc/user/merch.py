import functools

from flask import render_template, flash, g, redirect, url_for

from ..config import *
from ..util.db import fetch_all, fetch_one, insert_dict
from ..util.form import Field, validate
from . import bp


def is_merch_open() -> bool:
    return MERCH_OPEN < NOW() < MERCH_CLOSE


def merch_open(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not is_merch_open():
            flash('当前不在订购时间！')
            return redirect(url_for('.merch'))
        return view(*args, **kwargs)
    return wrapped


def _validate_buy() -> dict | None:
    if not (form := validate(
        Field('商品名', 'name', 1, 999, str, True),
        Field('型别', 'sku', 1, 100, str, True),
        Field('数量', 'quantity', 1, 3, int, lambda x: 0 < x < 100),
    )):
        return
    if not (item := INVENTORY.get(form['name'])):
        flash('商品不存在！')
        return
    if form['sku'] not in item.sku:
        flash('型别不存在！')
        return
    return form


@bp.post('/merch/buy')
@merch_open
def post_merch_buy():
    if form := _validate_buy():
        insert_dict('billing', {
            'uid': g.uid,
            'category': '纪念品',
            'item': form['name'],
            'spec': form['sku'],
            'quantity': form['quantity'],
            'price': INVENTORY[form['name']].price
        })
        flash('已添加至购物车！')
    return redirect(url_for('.merch'))


@bp.post('/merch/remove/<int:bid>')
@merch_open
def post_merch_remove(bid: int):
    cur = g.db.execute(  # you must be very careful letting user delete billing item
        'DELETE FROM billing WHERE bid = ? AND uid = ? ' \
        'AND category = "纪念品" AND t > ? AND t < ? AND fulfilled = 0',
        (bid, g.uid, int(MERCH_OPEN.timestamp()), int(MERCH_CLOSE.timestamp()))
    )
    g.db.commit()
    if cur.rowcount:
        flash('删除成功！')
    else:
        flash('删除失败！商品已交付制作或记录不存在。')
    return redirect(url_for('.merch'))


@bp.post('/merch/address')
def post_merch_address():
    if form := validate(
        Field('收货地址', 'address', 10, 200, str, True),
        Field('收货电话', 'phone', 5, 20, str, True),
        Field('收货人', 'name', 1, 10, str, True),
    ):
        insert_dict('address', form|{'uid': g.uid})
        flash('保存成功！')
    return redirect(url_for('user.merch'))


@bp.get('/merch')
def merch():
    is_open = is_merch_open()
    form = fetch_one('address', {'uid': g.uid})
    items = list(filter(  # only show items in this round of sale
        lambda x: MERCH_OPEN.timestamp() < x['t'] < MERCH_CLOSE.timestamp(),
        fetch_all('billing', {'uid': g.uid, 'category': '纪念品'}),
    ))
    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template(
        'merch.html', is_open=is_open, items=items, total=total, form=form,
    )
