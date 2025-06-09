import secrets
from time import time

from flask import session, g

from ..config import *
from .db import fetch_one, insert_dict
from . import bp


@bp.before_app_request
def check_grant():
    # ensure basic attrs exist
    g.uid = None
    g.roles = []
    try:
        if not (grant := fetch_one('grant', {'id': session['id']})):
            return  # not necessarily invalid, maybe just no grant
        if time() > grant['t'] + SESSION_EXPIRY.total_seconds():
            raise ValueError('session expired')
        if grant['user'] and (user := fetch_one('user', {'uid': grant['user']})):
            for k, v in user.items():
                setattr(g, k, v)  # load user info (uid, type, identity, nick)
        g.roles = list(filter(bool, grant['roles'].split(',')))
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
