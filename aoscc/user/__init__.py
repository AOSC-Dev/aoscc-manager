import functools
from flask import Blueprint, Response, g, render_template, request, redirect, url_for, session

from ..config import *
from ..util.db import fetch_one

bp = Blueprint('user', __name__)


@bp.before_app_request
def load_user():
    g.user = fetch_one('user', {'uid': session.get('uid')})
    g.uid = g.user['uid'] if g.user else None
    g.roles = set()
    if g.user:
        for typ, identity, roles in AUTO_ADMIN:
            if g.user[typ] == identity:
                g.roles.update(roles)

@bp.after_app_request
def log_trace_header(response: Response):
    response.headers.add('X-Log-Trace', f'{g.uid or 0}')
    return response


@bp.before_request
def user_check():
    register = fetch_one('register', {'uid': g.uid}) if g.uid else None
    g.registered = bool(register)
    g.confirmed = bool(register and register['confirmed'])
    g.arrived = bool(register and register['arrived'])


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.uid:
            session['login_return'] = request.url
            return redirect(url_for('user.login'))
        return view(*args, **kwargs)
    return wrapped

def nick_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user['nick']:
            return redirect(url_for('user.info'))
        return view(*args, **kwargs)
    return login_required(wrapped)

def registered_only(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.registered:
            return redirect(url_for('user.register'))
        return view(*args, **kwargs)
    return nick_required(wrapped)

def confirmed_only(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.confirmed:
            return redirect(url_for('user.index'))
        return view(*args, **kwargs)
    return registered_only(wrapped)

def arrived_only(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not g.arrived:
            return redirect(url_for('user.index'))
        return view(*args, **kwargs)
    return confirmed_only(wrapped)


@bp.get('/')
@registered_only
def index():
    return render_template('user/index.html', is_volunteer=volunteer.is_volunteer())


from . import login, info, register, pass_, badge, volunteer, vote, draw, pgp
