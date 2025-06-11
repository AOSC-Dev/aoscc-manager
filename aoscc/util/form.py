import re
from datetime import datetime
from collections import namedtuple

from flask import request, flash

Field = namedtuple('Field', 'display,name,minlen,maxlen,factory,condition')


def validate(*fields: Field, show_flash: bool = True) -> dict | None:
    def my_flash(msg: str):
        if show_flash:  # flash suppressor
            flash(msg)
    ret = {}
    for field in fields:
        val = request.form.get(field.name, '').strip()
        try:
            # 1. string length check
            if not field.minlen <= len(val) <= field.maxlen:
                raise ValueError()
            # 2. typed factory construct
            typed_val = field.factory(val)
            # 3. build cond func
            cond = field.condition
            if cond is True:
                cond = lambda _: True
            if isinstance(cond, str):
                cond = lambda x, pattern=cond: bool(re.fullmatch(pattern, x))
            # 4. cond check
            if not cond(typed_val):
                raise ValueError()
            # 5. add to result
            ret[field.name] = typed_val
        except Exception:
            if field.display.endswith('！'):
                my_flash(field.display)  # customized error msg
            else:
                my_flash(f'{field.display}格式错误！')
            return
    if not ret:
        my_flash('无效表单。')
        return
    return ret


def parse_date(s: str):
    return datetime.strptime(s, '%Y-%m-%d').date()
