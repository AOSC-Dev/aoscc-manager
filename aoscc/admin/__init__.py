from flask import Blueprint, render_template, redirect, url_for, session

from ..util.grant import check_role, revoke_client

bp = Blueprint('admin', __name__)


from . import grant, payment, notify, user, db, vote, draw


@bp.get('/')
def index():
    return render_template('admin/index.html')


@bp.get('/revoke')
def revoke():
    revoke_client(session['id'])
    return redirect(url_for('admin.index'))


@bp.route('/checkin/<string:token>')
@check_role('checkin')
def do_checkin(token: str):  # TODO
    raise NotImplementedError


"""
TODO:
roles = checkin,draw

签到子系统（志愿者登录，生成签到码，读取用户信息）
抽奖子系统（熵源、生成报告）
"""