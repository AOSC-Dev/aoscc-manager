from flask import render_template

from . import bp


@bp.get('/accommo')
def accommo():
    return render_template('service.html')
