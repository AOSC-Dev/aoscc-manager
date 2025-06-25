import re
import sys
import secrets
import functools
from time import time

from flask import session, g, flash, redirect, url_for

from ..config import *
from .db import fetch_one, fetch_all, insert_dict, delete_from
from . import bp


@bp.before_app_request
def check_grant():
    # ensure basic attrs exist
    g.uid = None
    g.roles = set()
    try:
        if not (grant := fetch_one('grant', {'id': session['id']})):
            return  # not necessarily invalid, maybe just no grant
        if time() > grant['t'] + SESSION_EXPIRY.total_seconds():
            raise ValueError('session expired')
        # THE LINE BELOW IS FOR DEBUGGING ONLY
        # grant['user'] = __import__('random').choice(fetch_all('register'))['uid']
        if grant['user'] and (user := fetch_one('user', {'uid': grant['user']})):
            for k, v in user.items():
                setattr(g, k, v)  # load user info (uid, type, identity, nick, remarks)
        g.roles = set(filter(bool, grant['roles'].split(',')))
    except Exception:
        # id not set or expired, reset new id
        session['id'] = secrets.token_hex(16)
        session.permanent = True


def update_grant():
    insert_dict('grant', {
        'id': session['id'],
        'user': g.uid,
        'roles': ','.join(g.roles),
    })


def has_role(role: str) -> bool:
    if role == '*':
        return bool(g.roles)
    return role in g.roles or 'admin' in g.roles


@bp.app_context_processor
def inject_has_role():
    return dict(has_role=has_role)


def check_role(role):
    def wrapper(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if not has_role(role):
                flash('角色权限不足。')
                return redirect(url_for('admin.index'))
            return view(*args, **kwargs)
        return wrapped
    return wrapper


def add_role(client_id: str, role: str):
    row = fetch_one('grant', {'id': client_id}) or {
        'id': client_id,
        'user': None,
        'roles': ''
    }
    row['roles'] = ','.join(
        set(filter(bool, row['roles'].split(','))) | {role}
    )
    insert_dict('grant', row)


def revoke_client(client_id: str = None):
    delete_from('grant', {'id': client_id or session['id']})


####################################################

def enroll_admin():  # INTENDED FOR COMMAND-LINE
    print('[ ENROLL NEW ADMIN ]')
    if len(sys.argv) > 2:
        client_id = sys.argv[2]
    else:
        client_id = input('Requesting Client ID: ')
    if not re.fullmatch(r'[0-9a-f]{32}', client_id):
        print('Invalid Client ID!')
        return
    from .. import make_app
    app = make_app()
    with app.test_request_context('/'):
        app.preprocess_request() 
        add_role(client_id, 'admin')
        print('Success!')
