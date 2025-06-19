import random
from math import sqrt, ceil

from flask import render_template, flash, redirect, url_for, g

from ..config import *
from ..util.db import query_all, fetch_all, fetch_one, insert_dict
from ..util.form import Field, validate
from ..util.grant import check_role
from . import bp


@bp.post('/draw/<int:did>/end')
@check_role('draw')
def post_draw_end(did: int):
    if not (current := fetch_one('draw_info', {'did': did})):
        flash('抽奖不存在！')
    elif current['ended']:
        flash('抽奖已经结束！')
    else:
        try:
            g.db.execute('BEGIN EXCLUSIVE')
            tkts = fetch_all('draw_detail', {'did': did})
            tkts = sorted(tkts, key=lambda x: x['uid'])
            seed = bytes.fromhex(''.join(tkt['color'][1:] for tkt in tkts))
            win_tkts = random.Random(seed).sample(tkts, min(current['count'], len(tkts)))
            for win_tkt in win_tkts:
                win_tkt['win'] = 1
                insert_dict('draw_detail', win_tkt, commit=False)
            current['ended'] = 1
            insert_dict('draw_info', current, commit=False)
        except Exception:
            g.db.rollback()
            flash('结束抽奖失败！')
        finally:
            g.db.commit()

    return redirect(url_for('admin.draw', did=did))


@bp.post('/draw/new')
@check_role('draw')
def post_new_draw():
    if form := validate(
        Field('奖品', 'title', 1, 50, str, True),
        Field('份数', 'count', 1, 3, int, lambda x: 1<=x<=100),
    ):
        rowid = insert_dict('draw_info', form)
    return redirect(url_for('admin.draw', did=rowid))


@bp.get('/draw/<int:did>')
@bp.get('/draw', defaults={'did': None})
@check_role('draw')
def draw(did: int = None):
    draws = fetch_all('draw_info')
    current = None
    if did and not (current := fetch_one('draw_info', {'did': did})):
        flash('抽奖不存在！')
        return redirect(url_for('admin.draw'))

    return render_template('admin/draw.html', draws=draws, current=current)


@bp.get('/draw/<int:did>/live')
@bp.get('/draw/live', defaults={'did': None})
@check_role('draw')
def draw_live(did: int = None):
    if did is not None:
        current = fetch_one('draw_info', {'did': did})
    else:
        current = (query_all('SELECT * FROM draw_info ORDER BY did DESC LIMIT 1') or [None])[0]
    if not current:
        flash('抽奖不存在！')
        return redirect(url_for('admin.draw'))

    tkts = query_all(
        'SELECT nick,color,win FROM draw_detail JOIN user USING(uid)' \
        ' WHERE did = ? ORDER BY uid',
        (current['did'],),
    )
    seed = bytes.fromhex(''.join(tkt['color'][1:] for tkt in tkts))
    rowsize = ceil(sqrt(len(tkts)))

    return render_template(
        'admin/draw-live.html',
        current=current, tkts=tkts, seed=seed, rowsize=rowsize,
    )
