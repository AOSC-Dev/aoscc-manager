from time import time
from pathlib import Path

from flask import render_template, redirect, url_for, session, flash, request, send_file, current_app

from ..config import *
from ..util.db import fetch_all, insert_dict, fetch_one
from ..util.form import Field, validate
from ..util.grant import check_role, has_role
from ..util.verify import verify_msg
from . import bp


def _get_pickup(uid: int, bid: int = None):
    return {
        row['bid']: row for row in
        fetch_all('billing', {
            'uid': uid,
            'category': '纪念品',
            'status': 1,
        } | ({'bid': bid} if bid else {}))
    }


@bp.post('/checkin/<int:uid>/pickup/<int:bid>')
@bp.post('/checkin/<int:uid>/pickup/all', defaults={'bid': None})
@check_role('checkin')
def post_merch_pickup(uid: int, bid: int):
    if bid:
        if not (item := _get_pickup(uid, bid).get(bid)):
            flash('指定的项目不存在或状态错误！')
        else:
            item['status'] = 2
            insert_dict('billing', item)
    else:
        for item in _get_pickup(uid).values():
            item['status'] = 2
            insert_dict('billing', item)
    return redirect(url_for('admin.checkin', uid=uid))


@bp.post('/checkin/<int:uid>')
@check_role('checkin')
def post_checkin_user(uid: int):
    # if user not exist, error will arise after redirect anyway
    if (row := fetch_one('register', {'uid': uid})) and (form := validate(
        Field('操作', 'action', 1, 10, str, ('checkin', 'cancel', 'save')),
        Field('会务备注', 'remarks', 0, 500, str, True),
    )):
        match form['action']:
            case 'checkin':
                row['arrived'] = int(time())
            case 'cancel':
                row['arrived'] = 0
            case 'save':
                row['remarks'] = form['remarks']
                flash('已保存！')
        insert_dict('register', row)

    return redirect(url_for('admin.checkin', uid=uid))


@bp.get('/checkin/<string:token>')
@bp.post('/checkin', defaults={'token': None})
#@check_role('checkin')  # see below
def post_checkin(token: str):
    if not has_role('checkin'):
        if token and request.method == 'GET':
            return render_template('admin/checkin-401.html')
        flash('角色权限不足。')
        return redirect(url_for('admin.index'))
    token = request.form.get('token', token)
    try:
        if not isinstance(token, str):
            raise AssertionError
        else:
            token = token.removeprefix(URL_BASE+url_for('admin.post_checkin')+'/')
            typ, msg = verify_msg(token)
            if typ != 'checkin':
                raise AssertionError
            session['_last_checkin_token'] = token
            return redirect(url_for('admin.checkin', uid=int(msg)))
    except AssertionError:
        flash('无效签到码！')
        return redirect(url_for('admin.checkin'))


@bp.get('/checkin/<int:uid>/badge')
@check_role('checkin')
def checkin_badge(uid: int):
    return send_file(Path(current_app.instance_path) / 'badges' / f'{uid}.png', 'image/png')


@bp.get('/checkin/<int:uid>')
@bp.get('/checkin', defaults={'uid': None})
@check_role('checkin')
def checkin(uid: int):
    if uid is not None:
        scanned = (('checkin', str(uid)) == verify_msg(session.get('_last_checkin_token')))
        if not (row := fetch_one('register JOIN user USING(uid)', {'uid': uid})):
            flash('用户不存在！')
            return redirect(url_for('admin.checkin'))
        volunteer = fetch_one('volunteer', {'uid': uid, 'status': 1})
        accommo = fetch_one('accommo', {'uid': uid})
        badge = fetch_one('badge', {'uid': uid})
        merch = _get_pickup(uid).values()
        shipped = fetch_all('billing', {'uid': uid, 'category': '纪念品', 'status': 2})
    return render_template('admin/checkin.html', **locals())
