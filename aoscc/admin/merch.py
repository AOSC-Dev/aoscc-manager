from collections import defaultdict

from flask import render_template

from ..config import *
from ..util.db import query_all
from ..util.grant import check_role
from . import bp


@bp.get('/merch')
@check_role('merch')
def merch():
    res = sorted(query_all(
        'SELECT item,spec,SUM(quantity) AS count FROM billing ' \
        'WHERE category = "纪念品" GROUP BY item,spec ORDER BY item, spec'
    ), key=lambda x: (
        (
            list(INVENTORY.keys()).index(x['item']),
            list(INVENTORY[x['item']].sku).index(x['spec']),
        )
        if (_ := INVENTORY.get(x['item'])) and _.sku.get(x['spec']) is not None
        else (-1, -1)
    ))

    stat = defaultdict(dict)
    for row in res:
        stat[row['item']][row['spec']] = row['count']
    overview = {k: sum(v.values()) for k, v in stat.items()}

    return render_template('admin/merch.html', overview=overview, stat=stat)
