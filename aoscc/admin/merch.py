from collections import defaultdict

from flask import render_template, request, redirect, url_for, flash

from ..config import *
from ..util.db import query_all, fetch_one, delete_from, update_table
from ..util.tmpl import dt2datetime
from ..util.grant import check_role
from .notify import enqueue_notify_quick
from . import bp


@bp.post('/merch/<int:uid>/ship')
@check_role('merch')
def post_merch_ship(uid: int):
    track = request.form.get('track') or f'当面交付于 {dt2datetime(NOW())}'
    shipped = []
    for bid in request.form.getlist('bid'):
        try:
            bid = int(bid)
            if update_table(
                'billing',
                {'status': 2, 'track': track},
                {'bid': bid, 'uid': uid, 'category': '纪念品', 'status': 1}
            ) != 1:
                raise ValueError()
            row = fetch_one('billing', {'bid': bid, 'uid': uid})
            shipped.append(
                f'{row['quantity']}x {row['item']}'+
                (f'（{row['spec']}）' if row['spec'] else '')
            )
        except Exception as exc:
            print(repr(exc))
            flash(f'订单 {bid} 发货失败！')
    if shipped:
        enqueue_notify_quick(
            uid, '订单发货通知',
            f'您预订的下列产品已通过 {track} 发货：\n\n' + '\n'.join(shipped) +
            '\n\n如有疑问，请回复本消息以联系会务组查询。'
        )
    return redirect(url_for('admin.user', uid=uid))


@bp.post('/merch/<int:uid>/<int:bid>/cancel')
@check_role('merch')
def post_merch_cancel(uid: int, bid: int):
    cond = {'bid': bid, 'uid': uid, 'category': '纪念品', 'status': 0}
    row = fetch_one('billing', cond)
    if delete_from('billing', cond):
        item_name = row['item'] + (f'（{row['spec']}）' if row['spec'] else '')
        enqueue_notify_quick(
            uid, '订单取消通知',
            f'我们已取消您订购的 {row['quantity']} 件{item_name}，'
            '可能是因为预订截止时您仍未付款或者其他原因。\n\n'
            '如需退款或有其他疑问，请回复本消息以联系会务组查询。'
        )
    else:
        flash('取消失败！')
    return redirect(url_for('admin.user', uid=uid))


@bp.get('/merch')
@check_role('merch')
def merch():
    res = sorted(query_all(
        'SELECT item,spec,status,SUM(quantity) AS count FROM billing ' \
        'WHERE category = "纪念品" GROUP BY item,spec,status'
    ), key=lambda x: (
        (
            list(INVENTORY.keys()).index(x['item']),
            list(INVENTORY[x['item']].sku).index(x['spec']),
        )
        if (_ := INVENTORY.get(x['item'])) and _.sku.get(x['spec']) is not None
        else (-1, -1)
    ))
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for row in res:
        # per spec
        stat[row['item']][row['spec']][row['status']] += row['count']
        stat[row['item']][row['spec']][None         ] += row['count']
        # per item
        stat[row['item']][None       ][row['status']] += row['count']
        stat[row['item']][None       ][None         ] += row['count']
        # overview
        stat[None       ][row['item']][row['status']] += row['count']
        stat[None       ][row['item']][None         ] += row['count']
        # grand total
        stat[None       ][None       ][row['status']] += row['count']
        stat[None       ][None       ][None         ] += row['count']

    return render_template('admin/merch.html', stat=stat)
