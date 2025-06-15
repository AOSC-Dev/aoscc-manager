from flask import render_template, flash, redirect, url_for, g, request

from ..config import *
from ..util.db import query_all, insert_dict, fetch_all
from ..util.form import Field, validate
from . import bp, check_role


def enqueue_notify(uid: int, title: str, content: str):
    return insert_dict('notify', {
        'uid': uid,
        'title': title,
        'content': content,
    })


def enqueue_notify_quick(uid: int, title_suf: str, content_body: str):
    return enqueue_notify(
        uid, f'{TITLE} {title_suf}',
        f'您好，\n\n{content_body}\n\n\n{TITLE} 会务组'
    )


@bp.post('/notify')
@check_role('notify')
def post_notify():
    if form := validate(
        Field('目标用户', 'uids', 1, 9999, str, r'\d+(,\d+)*,?'),
        Field('标题', 'title', 0, 200, str, True),
        Field('内容', 'content', 1, 1000, str, True),
    ):
        uids = set(map(int, filter(bool, form['uids'].split(','))))
        for uid in uids:
            try:
                enqueue_notify(uid, form['title'] or f'{TITLE} 系统通知', form['content'])
            except Exception:
                flash(f'用户 {uid} 不存在！')
        flash('提交的任务已加入队列！')
    return redirect(url_for('.notify'))


@bp.post('/notify/flush')
@check_role('notify')
def post_notify_flush():
    g.db.execute('DELETE FROM notify WHERE retry >= 3')
    g.db.commit()
    flash('已清空！')
    return redirect(url_for('.notify'))


@bp.get('/notify')
@check_role('notify')
def notify():
    in_progress = query_all('SELECT COUNT(*) AS cnt FROM notify WHERE retry < 3')[0]['cnt']
    failed = query_all('SELECT * FROM notify JOIN user USING(uid) WHERE retry >= 3')
    
    match request.args.get('uids', ''):
        case '':
            uids = ''
        case 'all_user':
            uids = ','.join([str(u['uid']) for u in fetch_all('user', {})])
        case 'all_registered':
            uids = ','.join([str(u['uid']) for u in fetch_all('register', {})])
        case 'all_arrived':
            uids = ','.join([str(u['uid']) for u in fetch_all('register', {'arrived': 1})])
        case 'all_accommo':
            uids = ','.join([str(u['uid']) for u in fetch_all('accommo', {})])
        case 'all_volunteer':
            uids = ','.join([str(u['uid']) for u in fetch_all('volunteer', {})])
        case _:
            uids = request.args['uids']
    return render_template('notify.html', uids=uids, in_progress=in_progress, failed=failed)


########## ABOVE: Flask Part ##########
########## BELOW: Notify Daemon ##########

import secrets
import sqlite3
from time import sleep
from pathlib import Path

from ..util.tg import send_telegram
from ..util.mail import send_email


def send_notify(task: dict):
    match task['type']:
        case 'telegram':
            return send_telegram(
                int(task['identity']),
                f'<b><u>{task['title']}</u></b>\n\n{task['content']}'
            )
        case 'email':
            return send_email(task['identity'], task['title'], task['content'])
        case _:
            return False


def notify_main():
    from .. import make_app
    db = sqlite3.connect(Path(make_app().instance_path) / 'aoscc.sqlite')
    db.row_factory = sqlite3.Row
    worker_id = secrets.token_hex(8)
    while True:
        cur = db.execute('SELECT * FROM notify JOIN user USING(uid) ' \
                        'WHERE lock IS NULL AND retry < 3 ORDER BY retry ASC ' \
                        'LIMIT 1')  # get next task
        if task := cur.fetchone():
            db.execute('BEGIN EXCLUSIVE')  # CRITICAL section
            locking = db.execute(  # lock task
                'UPDATE notify SET lock = ? WHERE nid = ? AND lock IS NULL',
                (worker_id, task['nid']),
            )
            db.commit()  # CRITICAL section end
            if not locking.rowcount:  # check if lock successful
                continue
            if send_notify(task):
                # remove task
                db.execute('DELETE FROM notify WHERE nid = ?', (task['nid'],))
            else:
                db.execute(  # add retry and release lock
                    'UPDATE notify SET retry = retry + 1, lock = NULL WHERE nid = ?',
                    (task['nid'],),
                )
            db.commit()
            sleep(1)  # next task after 1s
        else:
            sleep(10)  # idle 10s if no tasks
