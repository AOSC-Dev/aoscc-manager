import random

from flask import render_template, g, flash, redirect, url_for

from ..config import *
from ..util.db import fetch_one, fetch_all, insert_dict
from ..util.form import Field, validate
from . import bp, check_arrived


@bp.post('/draw/<int:did>')
@check_arrived
def post_draw(did: int):
    if not (draw := fetch_one('draw_info', {'did': did})):
        flash('抽奖不存在！')
    elif draw['ended']:
        flash('抽奖已结束！')
    elif form := validate(
        Field('颜色', 'color', 7, 7, str, r'#[0-9a-f]{6}'),
    ):
        insert_dict('draw_detail', form|{'uid': g.uid, 'did': did})
    return redirect(url_for('service.draw'))


@bp.get('/draw')
@check_arrived
def draw():
    actives = fetch_all('draw_info', {'ended': 0})
    mytkts = {
        row['did']: row for row in
        fetch_all('draw_detail JOIN draw_info USING(did)', {'uid': g.uid})
    }
    return render_template(
        'service/draw.html',
        actives=actives, mytkts=mytkts, rand=random.randbytes(3).hex(),
    )
