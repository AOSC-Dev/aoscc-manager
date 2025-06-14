import hashlib

from flask import render_template, g

from ..config import *
from ..util.db import fetch_all
from . import bp


def get_payment_hash(uid: int, type: str, identity: str, **_) -> str:
    acct = f'{type}:{identity}'
    hash = hashlib.sha256(acct.encode()).digest().hex()[-4:].upper()
    return f'{uid}:{hash}'


@bp.get('/billing')
def billing():
    items = fetch_all('billing', {'uid': g.uid})
    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template(
        'billing.html', items=items, total=total,
        hash=get_payment_hash(g.uid, g.type, g.identity),
    )

