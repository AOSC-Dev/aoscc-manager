import functools

from flask import Blueprint, render_template, redirect, url_for, flash, g, session

bp = Blueprint('service', __name__)

from ..util.db import delete_from
from ..user import user_check


@bp.before_request
def register_check():
    if ret := user_check():
        return ret
    if not g.registered:  # all module require registration
        return redirect(url_for('user.register'))


def check_arrived(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.arrived:
            flash('您尚未签到！')
            return redirect(url_for('service.index'))
        return view(*args, **kwargs)
    return wrapped


from . import checkin, badge, volunteer, pgp, accommo, vote, draw


@bp.get('/service')
def index():
    return render_template('service/index.html')


@bp.post('/service/cancel')
def post_cancel():
    if g.arrived:
        flash('您已完成签到，无法取消注册！')
        return redirect(url_for('service.index'))
    if volunteer.is_volunteer():
        flash('您是已确认的志愿者，无法取消注册！请先联系会务组取消志愿者状态。')
        return redirect(url_for('service.index'))
    if accommo.is_booked():
        flash('您已预订协议酒店，无法取消注册！请先至预订页面取消。')
        return redirect(url_for('service.index'))
    badge.post_badge_del()  # need to delete PNG file
    delete_from('register', {'uid': g.uid})  # most tables will CASCADE delete
    session.pop('_flashes', None)  # clear repetitive msg
    flash('取消成功！')
    return redirect(url_for('user.register'))
