from flask import render_template, flash, redirect, url_for

from ..config import *
from ..util.db import fetch_one, query_all, insert_dict, delete_from
from ..util.form import Field, validate
from . import bp, check_role


@bp.post('/grant')
@check_role('admin')
def post_grant():
    if form := validate(
        Field('客户端 ID', 'id', 32, 32, str, r'[0-9a-f]{32}'),
        Field('授予角色', 'role', 0, 20, str, r'[a-z]+'),
    ):
        if not form['role']:
            delete_from('grant', {'id': form['id']})
            flash('撤销成功！')
        else:
            row = fetch_one('grant', {'id': form['id']})
            if not row:
                row = {'id': form['id'], 'user': None, 'roles': ''}
            row['roles'] = ','.join(
                list(filter(bool, row['roles'].split(','))) + [form['role']]
            )
            insert_dict('grant', row)
            flash('授权成功！')
    return redirect(url_for('.grant'))


@bp.get('/grant')
@check_role('admin')
def grant():
    admins = query_all('SELECT id,roles FROM grant WHERE roles != ""')
    return render_template('grant.html', admins=admins)
