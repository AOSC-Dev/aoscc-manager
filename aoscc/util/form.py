import re
from datetime import datetime
from collections import namedtuple

from flask import request, flash

Field = namedtuple('Field', 'display,name,minlen,maxlen,factory,condition')


def validate(*fields: Field, form: dict = None) -> dict | None:
    form = form or request.form
    ret = {}
    for field in fields:
        val = form.get(field.name, '').strip()
        try:
            # 1. string length check
            if not field.minlen <= len(val) <= field.maxlen:
                raise ValueError()
            # 2. typed factory construct
            typed_val = field.factory(val)
            # 3. build cond func
            cond = field.condition
            if not typed_val or cond is True:
                cond = lambda _: True
            if isinstance(cond, str):
                cond = (cond,)
            if isinstance(cond, tuple):
                cond = lambda x, ptns=cond: any(re.fullmatch(ptn, x) for ptn in ptns)
            # 4. cond check
            if not cond(typed_val):
                raise ValueError()
            # 5. add to result
            ret[field.name] = typed_val
        except Exception:
            if field.display.endswith('！'):
                flash(field.display)  # customized error msg
            else:
                flash(f'{field.display}格式错误！')
            return
    if not ret:
        flash('无效表单。')
        return
    return ret


def parse_date(s: str):
    return datetime.strptime(s, '%Y-%m-%d').date()
