from flask import Blueprint, render_template, redirect, url_for, flash, g, session

bp = Blueprint('service', __name__, template_folder='templates')

from ...util.db import delete_from
from ..register import is_registered
from . import checkin, badge, volunteer, pgp, accommo


@bp.get('/service')
def index():
    return render_template('service.html')


@bp.post('/service/cancel')
def post_cancel():
    if checkin.is_checked_in():
        flash('您已完成签到，无法取消！')
        return redirect(url_for('.index'))
    if volunteer.is_volunteer():
        flash('您是已确认的志愿者，无法取消！请先联系会务组取消志愿者状态。')
        return redirect(url_for('.index'))
    # 已预订住宿?
    badge.post_badge_del()  # need to delete PNG file
    delete_from('register', {'uid': g.uid})  # most tables will CASCADE delete
    session.pop('_flashes', None)  # clear repetitive msg
    flash('取消成功！')
    return redirect(url_for('user.register'))


@bp.before_request
def register_check():
    if not is_registered():  # all module require registration
        return redirect(url_for('user.register'))
