from flask import Blueprint, render_template, redirect, url_for, session

from ..util.grant import check_role, revoke_client

bp = Blueprint('admin', __name__, template_folder='templates')


@bp.get('/')
def index():
    return render_template('admin.html')


@bp.get('/revoke')
def revoke():
    revoke_client(session['id'])
    return redirect(url_for('.index'))


@bp.route('/checkin/<string:token>')
@check_role('checkin')
def do_checkin(token: str):  # TODO
    raise NotImplementedError


from . import grant, payment, notify, user, db, vote



"""
TODO:
roles = checkin,vote,draw

签到子系统（志愿者登录，生成签到码，读取用户信息）
抽奖子系统（熵源、生成报告）
投票子系统（表决器）
"""