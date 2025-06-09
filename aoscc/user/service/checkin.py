import base64
from io import BytesIO

from flask import render_template, g, url_for
import qrcode

from ...config import *
from ...util.db import fetch_one
from ...util.verify import sign_msg
from . import bp


def is_checked_in() -> bool:
    return bool((fetch_one('register', {'uid': g.uid}) or {}).get('arrived'))


@bp.get('/checkin')
def checkin():
    token = sign_msg('checkin', str(g.uid), 0)
    url = URL_BASE + url_for('admin.do_checkin', token=token)
    qr = qrcode.make(url, border=1)
    png = BytesIO()  # buffer in memory
    qr.save(png, format="png")
    b64png = base64.b64encode(png.getvalue()).decode()
    return render_template('checkin.html', qr=b64png)
