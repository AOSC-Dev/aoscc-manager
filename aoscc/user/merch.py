import functools

from flask import render_template, flash, g, redirect, url_for

from ..config import *
from ..util.db import fetch_all, fetch_one, insert_dict, query_all
from ..util.form import Field, validate
from . import bp


def _validate_buy() -> dict | None:
    if not (form := validate(
        Field('商品名', 'name', 1, 999, str, True),
        Field('型别', 'sku', 0, 100, str, True),
        Field('数量', 'quantity', 1, 3, int, lambda x: 0 < x < 100),
    )):
        return
    if not (item := INVENTORY.get(form['name'])):
        flash('商品不存在！')
        return
    if NOW() > item.cutoff:
        flash('该商品当前不可售！')
        return
    if form['sku'] not in item.sku:
        flash('型别不存在！')
        return
    return form


@bp.post('/merch/buy')
def post_merch_buy():
    if form := _validate_buy():
        stock = INVENTORY[form['name']].sku[form['sku']]
        try:
            g.db.execute('BEGIN EXCLUSIVE')
            orders = query_all(
                'SELECT SUM(quantity) AS cnt FROM billing WHERE category = "纪念品"'
                ' AND item = ? AND spec = ?', (form['name'], form['sku'])
            )
            if (orders[0]['cnt'] or 0) + form['quantity'] > stock:
                raise ValueError
            insert_dict('billing', {
                'uid': g.uid,
                'category': '纪念品',
                'item': form['name'],
                'spec': form['sku'],
                'quantity': form['quantity'],
                'price': INVENTORY[form['name']].price
            }, commit=False)
            flash('已添加至订单！')
        except Exception:
            g.db.rollback()
            flash('库存不足，订购失败！')
        finally:
            g.db.commit()
    return redirect(url_for('user.merch'))


@bp.post('/merch/remove/<int:bid>')
def post_merch_remove(bid: int):
    cur = g.db.execute(  # you must be very careful letting user delete billing item
        'DELETE FROM billing WHERE bid = ? AND uid = ? ' \
        'AND category = "纪念品" AND status = 0', (bid, g.uid),
    )
    g.db.commit()
    if cur.rowcount:
        flash('取消成功！')
    else:
        flash('取消失败！商品已交付生产或记录不存在。')
    return redirect(url_for('user.merch'))


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
    form = fetch_one('address', {'uid': g.uid})
    items = fetch_all('billing', {'uid': g.uid, 'category': '纪念品'})
    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template('user/merch.html', items=items, total=total, form=form)
