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
        'SELECT item,spec,status,SUM(quantity) AS count FROM billing ' \
        'WHERE category = "纪念品" GROUP BY item,spec,status'
    ), key=lambda x: (
        (
            list(INVENTORY.keys()).index(x['item']),
            list(INVENTORY[x['item']].sku).index(x['spec']),
        )
        if (_ := INVENTORY.get(x['item'])) and _.sku.get(x['spec']) is not None
        else (-1, -1)
    ))
    stat = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for row in res:
        # per spec
        stat[row['item']][row['spec']][row['status']] += row['count']
        stat[row['item']][row['spec']][None         ] += row['count']
        # per item
        stat[row['item']][None       ][row['status']] += row['count']
        stat[row['item']][None       ][None         ] += row['count']
        # overview
        stat[None       ][row['item']][row['status']] += row['count']
        stat[None       ][row['item']][None         ] += row['count']
        # grand total
        stat[None       ][None       ][row['status']] += row['count']
        stat[None       ][None       ][None         ] += row['count']

    return render_template('admin/merch.html', stat=stat)
