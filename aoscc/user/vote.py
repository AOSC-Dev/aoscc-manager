from flask import render_template, g, flash, redirect, url_for

from ..config import *
from ..util.db import fetch_one, fetch_all, insert_dict
from ..util.form import Field, validate
from . import bp, arrived_only


@bp.post('/vote/<int:vid>')
@arrived_only
def post_vote(vid: int):
    if not (voting := fetch_one('vote_info', {'vid': vid})):
        flash('投票不存在！')
    elif voting['ended']:
        flash('投票已结束！')
    elif form := validate(
        Field('投票选择', 'vote', 1, 2, int, (1,-1,0)),
    ):
        insert_dict('vote_detail', form|{'uid': g.uid, 'vid': vid})
    return redirect(url_for('user.vote'))


@bp.get('/vote')
@arrived_only
def vote():
    actives = fetch_all('vote_info', {'ended': 0})
    votes = {
        row['vid']: row for row in
        fetch_all('vote_detail JOIN vote_info USING(vid)', {'uid': g.uid})
    }
    return render_template('user/vote.html', actives=actives, votes=votes)
