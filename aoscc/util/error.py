from html import escape
from traceback import format_exception

from flask import render_template, redirect, request, make_response
from werkzeug.exceptions import InternalServerError

from ..config import *
from .tg import send_telegram
from . import bp


@bp.get('/_clear_cache')
def clear_cache():
    resp = redirect('/')
    # This header is a Baseline 2023 browser feature
    resp.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "*"'
    return resp


@bp.app_errorhandler(403)
@bp.app_errorhandler(404)
@bp.app_errorhandler(405)
def handle_404(exc):
    return make_response(render_template('error.html', error='404 未找到页面'), 404)


@bp.app_errorhandler(413)
def handle_413(exc):
    return make_response(render_template('error.html', error='413 上传文件过大'), 413)


@bp.app_errorhandler(500)
def handle_500(exc):
    if isinstance(exc, InternalServerError):
        exc = exc.original_exception
    msg = '#WEB_ERROR\n<pre>' + escape(
         f'Remote: {request.remote_addr}\n'
         f'Method: {request.method}\n'
         f'URL: {request.url}\n'
         f'Endpoint: {request.endpoint}\n'
         f'Exception: {repr(exc)}\n\n'
           + ''.join(format_exception(exc))
    ) + '</pre>'
    send_telegram(REPORTING_ID, msg)
    return make_response(render_template('error.html'), 500)
