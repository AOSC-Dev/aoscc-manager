from datetime import datetime

from flask import url_for

from ..config import *
from . import bp


@bp.app_context_processor
def inject_config():
    return dict(**ALL_CONFIG)


@bp.app_context_processor
def inject_contact_us():
    return dict(CONTACT_US=f'<a href="{ url_for('contact') }">联系会务组</a>')


@bp.app_template_filter('ts2dt')
def ts2dt(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


@bp.app_template_filter('date')
def dt2date(dt: datetime) -> str:
    return dt.strftime(r'%Y-%m-%d')


@bp.app_template_filter('datetime')
def dt2datetime(dt: datetime) -> str:
    return dt.strftime(r'%Y-%m-%d %H:%M:%S')


@bp.app_template_filter('uid_link')
def uid_link(uid: int) -> str:
    return f'<a target="_blank" href="{url_for('admin.user', uid=uid)}">{uid}</a>'
