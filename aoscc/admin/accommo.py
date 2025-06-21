from itertools import combinations
from collections import defaultdict

from flask import render_template, flash

from ..config import *
from ..util.db import query_all
from ..util.form import parse_date
from . import bp


def _get_diff(guests) -> int:
    dates = list(map(lambda guest: (  # parse checkin/out dates
        parse_date(guest['checkin']),
        parse_date(guest['checkout']),
    ), guests))
    earliest = min(x[0] for x in dates)  # room booked starting from
    latest = max(x[1] for x in dates)    # room released after
    total_slots = (latest-earliest).days*len(guests)      # days*guests
    occupied_slots = sum((x[1]-x[0]).days for x in dates) # actually used
    return total_slots - occupied_slots  # mismatching slots


def _process_shared_group(guests: list[dict], k: int) -> list[tuple[dict]]:
    # Note: This algorithm is not optimal, but might work well and make sense
    tolerance = 0  # tolerance of mismatching date slots
    ret = []  # result rooms
    while len(guests) >= k:  # we still have more than one room
        for comb in combinations(guests, k):  # comb of k guests
            if _get_diff(comb) <= tolerance:  # see if dates match *well*
                ret.append(comb)  # form a room
                for guest in comb:
                    guests.remove(guest)
                break    # restart from begining because 1. booking order 2. list changed
        else:
            tolerance += 1  # no pair found, increase tolerance next round
    if guests:  # remaining people goes into one room ...
        ret.append(guests)
    return ret


@bp.get('/accommo')
def accommo():
    vacancy = {name: type.vacancy for name, type in ROOM_OFFERING.items()}
    booking = query_all(
        'SELECT * FROM accommo JOIN billing USING(bid) JOIN user USING(uid)' \
        ' ORDER BY `type`, `group`, `t`'
    )
    pending = defaultdict(lambda: defaultdict(list))
    arrange = defaultdict(list)
    for row in booking:
        pending[row['type']][row['group']].append(row)
    for type, groups in pending.items():
        for group, guests in groups.items():
            if group.startswith('单独入住'):
                if len(guests) != 1:
                    flash(f'{group}组别不止一人！')
                arrange[type].append(guests)
            else:
                arrange[type].extend(_process_shared_group(guests, ROOM_OFFERING[type].nguest))
        vacancy[type] -= len(arrange[type])

    return render_template('admin/accommo.html', arrange=arrange, vacancy=vacancy)
