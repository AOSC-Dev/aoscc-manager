import base64
from io import BytesIO

from flask import render_template, g, url_for
import qrcode

from ..config import *
from ..util.crypt import sign_msg
from . import bp, confirmed_only


@bp.get('/pass', endpoint='pass')
@confirmed_only
def pass_():
    token = sign_msg('checkin', str(g.uid), 0)
    url = URL_BASE + url_for('admin.post_checkin', token=token)
    qr = qrcode.make(url, border=1)
    png = BytesIO()  # buffer in memory
    qr.save(png, format="png")
    b64png = base64.b64encode(png.getvalue()).decode()
    return render_template('user/pass.html', qr=b64png)
