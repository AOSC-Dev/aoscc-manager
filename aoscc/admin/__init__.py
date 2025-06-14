import functools

from flask import Blueprint, render_template, redirect, url_for, flash, g

from ..util.grant import update_grant

bp = Blueprint('admin', __name__, template_folder='templates')


def has_role(role: str) -> bool:
    return role in g.roles or 'admin' in g.roles


@bp.context_processor
def inject_has_role():
    return dict(has_role=has_role)


def check_role(role):
    def wrapper(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if not has_role(role):
                flash('角色权限不足。')
                return redirect(url_for('.index'))
            return view(*args, **kwargs)
        return wrapped
    return wrapper


@bp.get('/')
def index():
    return render_template('admin.html')


@bp.get('/revoke')
def revoke():
    g.uid = None
    g.roles = []
    update_grant()
    return redirect(url_for('.index'))


@bp.route('/checkin/<string:token>')
def do_checkin(token: str):  # TODO
    raise NotImplementedError


from . import grant, payment



"""
TODO:
roles = admin,cashier,checkin,vote,draw,notice

收款系统
签到子系统（志愿者登录，生成签到码，读取用户信息）
管理后台（列用户，入替）
通知子系统（队列重试，多选发送）
抽奖子系统（熵源、生成报告）
投票子系统（表决器）
"""