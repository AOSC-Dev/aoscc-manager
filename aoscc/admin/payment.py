from flask import render_template, redirect, url_for, session, flash, request

from ..config import *
from ..util.db import query_all, insert_dict, fetch_one
from ..util.form import Field, validate, parse_date
from ..user.billing import get_payment_hash
from .notify import enqueue_notify_quick
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
            if amount > 0:
                enqueue_notify_quick(
                    form['uid'], '支付确认回执',
                    f'我们已收到您于 {form['date'].strftime('%Y-%m-%d')} '
                    f'通过{form['provider']}支付的 {form['amount']} 元。',
                )
            else:
                enqueue_notify_quick(
                    form['uid'], '退款通知',
                    f'我们已于 {form['date'].strftime('%Y-%m-%d')} ' \
                    f'通过{form['provider']}向您发送退款 {form['amount'][1:]} 元，' # strip -
                    f'请注意查收。\n\n如您未收到该笔退款，请回复此消息联系会务组。',
                )
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


def _get_balance():
    return query_all('SELECT b.uid, u.nick, SUM(b.quantity*b.price) AS balance ' \
                     'FROM billing b JOIN user u USING(uid) ' \
                     'GROUP BY b.uid HAVING balance != 0 ORDER BY balance DESC')


@bp.post('/payment/notify/pay')
@check_role('payment')
def post_payment_notify_pay():
    for row in filter(lambda x: x['balance'] > 0, _get_balance()):
        enqueue_notify_quick(
            row['uid'], '待支付提醒',
            '您有已订购的纪念品或服务账单尚未付款，长时间未付款的订单可能被取消。\n\n'
            '如您已完整支付，请您登入系统检查订购和支付记录，若无法查询到您的付款记录，'
            '或者您在转账时忘记添加附言，请回复此消息提供转账回单，我们将尽快核对支付记录。'
        )
    flash('已加入通知队列。')
    return redirect(url_for('.payment'))


@bp.post('/payment/notify/refund')
@check_role('payment')
def post_payment_notify_refund():
    for row in filter(lambda x: x['balance'] < 0, _get_balance()):
        enqueue_notify_quick(
            row['uid'], '溢缴款提醒',
            '您向我们支付的数额已超出账单应付金额，请您登入系统检查账单中的订购和支付记录。\n\n'
            '如您忘记订购所支付的项目，请在截止时间前订购，您的溢缴款将自动抵扣其价格。\n\n'
            '如您需要退款，请回复此消息联系我们。'
        )
    flash('已加入通知队列。')
    return redirect(url_for('.payment'))


@bp.get('/payment')
@check_role('payment')
def payment():
    recent = query_all('SELECT * FROM billing JOIN user USING(uid) ' \
                       'WHERE category = "支付" ORDER BY bid DESC LIMIT 10')
    balance = _get_balance()
    return render_template('payment.html', recent=recent, balance=balance)
