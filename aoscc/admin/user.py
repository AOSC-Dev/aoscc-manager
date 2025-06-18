from flask import render_template

from ..config import *
from ..util.db import fetch_all
from ..util.grant import check_role
from . import bp


@bp.get('/user')
@check_role('*')
def user():
    users = fetch_all('user JOIN info USING(uid)')
    return render_template('admin/user.html', users=users)
