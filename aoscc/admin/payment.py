from flask import render_template, redirect, url_for, session, flash, request

from ..config import *
from ..util.db import query_all, insert_dict, fetch_one
from ..util.form import Field, validate, parse_date
from ..user.billing import get_payment_hash
from . import bp, check_role


@bp.post('/payment')
@check_role('payment')
def post_payment():
    if form := validate(
        Field('支付日期', 'date', 10, 10, parse_date, True),
        Field('支付方式', 'provider', 1, 10, str, ('微信', '支付宝')),
        Field('用户 ID', 'uid', 1, 10, int, lambda x: x>0),
        Field('金额', 'amount', 1, 10, str, r'\-?\d+(\.\d{1,2})?'),
    ):
        amt = form['amount'].split('.')
        amount = int(amt[0] + ((amt[1] if len(amt)>1 else '')+'00')[:2])
        try:
            insert_dict('billing', {
                't': int(form['date'].strftime('%s')),
                'uid': form['uid'],
                'category': '支付',
                'item': form['provider']+('支付' if amount>0 else '退款'),
                'spec': '',
                'quantity': 1,
                'price': -amount,
                'fulfilled': 1,
            })
            session['_payment_date'] = form['date'].strftime('%Y-%m-%d')
            session['_payment_provider'] = form['provider']
        except Exception:
            flash('录入失败！用户不存在？')
    return redirect(url_for('.payment'))


@bp.get('/payment/hash')
@check_role('payment')
def payment_hash():
    try:
        uid = int(request.args.get('uid', '0'))
        row = fetch_one('user', {'uid': uid})
        if not row:
            raise ValueError
        return get_payment_hash(**row).split(':')[1]
    except Exception:
        return 'USER NOT FOUND'


@bp.get('/payment')
@check_role('payment')
def payment():
    recent = query_all('SELECT * FROM billing JOIN user USING(uid) ' \
                       'WHERE category = "支付" ORDER BY bid DESC LIMIT 10')
    balance = query_all('SELECT b.uid, u.nick, SUM(b.quantity*b.price) AS balance ' \
                        'FROM billing b JOIN user u USING(uid) ' \
                        'GROUP BY b.uid HAVING balance != 0 ORDER BY balance DESC')
    return render_template('payment.html', recent=recent, balance=balance)
