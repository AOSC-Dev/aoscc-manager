from flask import render_template, flash, redirect, url_for, g

from ..config import *
from ..util.db import query_all, fetch_all, fetch_one, insert_dict
from ..util.form import Field, validate
from ..util.grant import check_role
from . import bp


@bp.post('/vote/<int:vid>/end')
@check_role('vote')
def post_vote_end(vid: int):
    if not (current := fetch_one('vote_info', {'vid': vid})):
        flash('投票不存在！')
    elif current['ended']:
        flash('投票已经结束！')
    else:
        try:
            g.db.execute('BEGIN EXCLUSIVE')
            result = {
                row['vote']: row['cnt']
                for row in query_all(
                    'SELECT vote, COUNT(*) AS cnt FROM vote_detail WHERE vid = ? GROUP BY vote',
                    (current['vid'],),
                )
            }
            current['ended'] = 1
            current['favor'] = result.get(1, 0)
            current['against'] = result.get(-1, 0)
            current['abstain'] = result.get(0, 0)
            insert_dict('vote_info', current, commit=False)
        except Exception:
            g.db.rollback()
            flash('结束投票失败！')
        finally:
            g.db.commit()
    return redirect(url_for('admin.vote', vid=vid))


@bp.post('/vote/new')
@check_role('vote')
def post_new_vote():
    if form := validate(
        Field('标题', 'title', 1, 50, str, True),
    ):
        rowid = insert_dict('vote_info', form)
    return redirect(url_for('admin.vote', vid=rowid))


@bp.get('/vote/<int:vid>')
@bp.get('/vote', defaults={'vid': None})
@check_role('vote')
def vote(vid: int = None):
    votings = fetch_all('vote_info')
    current = None
    if (vid is not None) and not (current := fetch_one('vote_info', {'vid': vid})):
        flash('投票不存在！')
        return redirect(url_for('admin.vote'))

    return render_template('admin/vote.html', votings=votings, current=current)


@bp.get('/vote/<int:vid>/live')
@bp.get('/vote/live', defaults={'vid': None})
@check_role('vote')
def vote_live(vid: int = None):
    if vid is not None:
        current = fetch_one('vote_info', {'vid': vid})
    else:
        current = (query_all('SELECT * FROM vote_info ORDER BY vid DESC LIMIT 1') or [None])[0]
    if not current:
        flash('投票不存在！')
        return redirect(url_for('admin.vote'))

    voters = query_all(
        'SELECT nick,vote FROM register' \
        ' JOIN user USING(uid) LEFT JOIN vote_detail' \
        ' ON vote_detail.uid = register.uid AND vote_detail.vid = ?' \
        ' WHERE arrived = 1 ORDER BY nick',
        (current['vid'],),
    )

    count = {
        vote: sum(vote == voter['vote'] for voter in voters)
        for vote in (1,-1,0)
    }

    return render_template(
        'admin/vote-live.html',
        current=current, voters=voters, count=count,
    )
