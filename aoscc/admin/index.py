from flask import render_template

from ..util.db import count_rows
from . import bp, check_role


@bp.get('/')
@check_role('*')
def index():
    n_users = count_rows('user')
    n_registered = count_rows('register')
    n_not_confirmed = count_rows('register', {'confirmed': 0})
    n_confirmed = n_registered - n_not_confirmed
    n_arrived = count_rows('register', {'arrived': 1})
    return render_template('admin/index.html', **locals())
