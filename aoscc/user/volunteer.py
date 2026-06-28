from flask import render_template, g, flash, redirect, url_for

from ..config import *
from ..util.db import fetch_one, insert_dict, delete_from
from ..util.form import Field, validate, parse_date
from . import bp, registered_only


@bp.post('/volunteer')
@registered_only
def post_volunteer():
    if not VOLUNTEER_OPEN:
        flash('志愿者报名已结束。')
    elif fetch_one('volunteer', {'uid': g.uid}):
        flash('信息已存在！')  # no silent update, status uncertain
    elif form := validate(
        Field('抵达日期', 'arrive', 10, 10, str, parse_date),
        Field('返程日期', 'depart', 10, 10, str, parse_date),
        Field('T 恤尺码', 'tshirt', 1, 3, str, r'([2-9]?X)?(S|M|L)'),
        Field('贡献者 ID', 'contrib', 0, 30, str, True),
        Field('其他信息', 'other', 0, 500, str, True),
    ):
        insert_dict('volunteer', form|{'uid': g.uid})
        flash('报名成功！请留意后续系统通知！')
    return redirect(url_for('user.volunteer'))


def is_volunteer() -> bool:
    return (fetch_one('volunteer', {'uid': g.uid}) or {}).get('status') == 1


@bp.post('/volunteer/cancel')
@registered_only
def post_volunteer_cancel():
    if is_volunteer():
        flash('您的申请已获会务组确认，请联系会务组取消！')
    else:
        delete_from('volunteer', {'uid': g.uid})
        flash('取消成功！')
    return redirect(url_for('user.volunteer'))


@bp.get('/volunteer')
@registered_only
def volunteer():
    form = fetch_one('volunteer', {'uid': g.uid})
    return render_template('user/volunteer.html', form=form)
