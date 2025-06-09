from itertools import batched

from flask import render_template, redirect, url_for, flash, g, abort, request, session

from ...util.db import fetch_all, fetch_one, insert_dict, delete_from
from ...util.form import Field, validate
from . import bp


def is_in_pgp_party(uid: int = None) -> bool:
    return bool(fetch_one('pgp_info', {'uid': uid or g.uid}))


@bp.post('/pgp')
def post_pgp():
    if is_in_pgp_party():  # no silent update, must revoke first
        flash('信息已存在！')
    elif form := validate(
        Field('密钥指纹', 'fpr', 40, 40, str, r'[0-9A-F]{40}'),
        Field('关联身份', 'keyuid', 1, 500, str, True),
        Field('必须阅知注意事项！', 'consent', 2, 2, str, lambda x: x=='on'),
    ):
        form.pop('consent', None)
        insert_dict('pgp_info', form|{'uid': g.uid})
        flash('保存成功！')
    return redirect(url_for('.pgp'))


@bp.post('/pgp/cancel')
def post_pgp_cancel():
    delete_from('pgp_info', {'uid': g.uid})  # will CASCADE signees
    return redirect(url_for('.pgp'))


def query_key(uid: int) -> dict:
    if (
        uid
        and (user := fetch_one('user', {'uid': uid}))
        and (key := fetch_one('pgp_info', {'uid': uid}))
    ):
        return {
            'nick': user['nick'],
            'fpr': fpr(key['fpr']),
            'keyuid': key['keyuid'],
        }
    else:
        return {}


@bp.get('/pgp/key')
def pgp_key():
    if ret := query_key(request.args.get('uid')):
        session['_last_query_key'] = ret
        return ret
    else:
        abort(404)


@bp.post('/pgp/sign')
def post_pgp_sign():
    if form := validate(
        Field('对方用户不存在！', 'signee', 1, 10, int, is_in_pgp_party),
        Field('验证等级', 'level', 1, 1, int, lambda x: 0<=x<=3),
    ):
        if form['signee'] == g.uid:
            flash('不要自己和自己签名玩啊...')
        elif session.get('_last_query_key', {}) != query_key(form['signee']):
            flash('待签署项目与最后查询不匹配！请刷新页面并重新进行验证！')
        else:
            insert_dict('pgp_sign', form|{'signer': g.uid})
            flash('保存成功！')
    session.pop('_last_query_key', None)
    return redirect(url_for('.pgp'))


@bp.post('/pgp/sign/del')
def post_pgp_sign_del():
    if form := validate(
        Field('对方用户不存在！', 'signee', 1, 10, int, is_in_pgp_party),
    ):
        delete_from('pgp_sign', form|{'signer': g.uid})
        flash('删除成功！')
    return redirect(url_for('.pgp'))


@bp.app_template_filter('fpr')
def fpr(fpr: str) -> str:  # magic, 0123ABCD to 0123 ABCD...
    return '\n'.join(map(' '.join, batched(map(''.join, batched(fpr, 4)), 5)))


@bp.get('/pgp')
def pgp():
    mykey = fetch_one('pgp_info', {'uid': g.uid})
    records = fetch_all(
        'pgp_sign JOIN pgp_info ON pgp_info.uid = pgp_sign.signee',
        {'signer': g.uid},
    )
    return render_template('pgp.html', mykey=mykey, records=records)
