from io import StringIO
from csv import DictWriter
from flask import render_template, request, make_response, flash

from ..config import *
from ..util.db import fetch_all, query_all
from ..util.form import Field, validate
from ..util.tmpl import ts2dt, dt2datetime
from ..util.encrypt import decrypt
from . import bp, check_role


@bp.route('/db', methods=['GET', 'POST'])
@check_role('admin')
def db():
    tables = sorted([
        row['name']
        for row in fetch_all('sqlite_master', {'type': 'table'})
    ])
    form = {}
    results = []
    if request.form and (form := validate(
        Field('SQL', 'sql', 1, 500, str, True),
        Field('解密密钥', 'sk', 0, 64, str, r'[0-9a-f]{64}'),
        Field('格式', 'format', 1, 10, str, ('display', 'csv')),
    )):
        try:
            results = query_all(form['sql'])  # excute query
        except Exception:
            flash('执行时出错！')
            results = []

        if results and 'legal_id' in results[0]:  # decrypt legal ID
            for row in results:
                if form['sk']:
                    row['legal_id'] = decrypt(row['legal_id'], form['sk'])
                else:
                    row['legal_id'] = '[ENCRYPTED]'
        if results and 't' in results[0]:  # format timestamp
            for row in results:
                row['t'] = dt2datetime(ts2dt(row['t']))

        if results and form['format'] == 'csv':  # make csv resnponse
            buffer = StringIO()  # buffer and return from memory
            csv = DictWriter(buffer, fieldnames=results[0].keys())
            csv.writeheader()
            csv.writerows(results)
            resp = make_response(buffer.getvalue())
            resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
            filename = f'aoscc-{NOW().strftime('%Y-%m-%d-%H-%M-%S')}.csv'
            resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return resp

    return render_template('db.html', tables=tables, form=form, results=results)
