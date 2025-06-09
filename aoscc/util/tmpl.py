from datetime import datetime

from ..config import *
from . import bp


@bp.app_context_processor
def inject_config():
    return dict(**ALL_CONFIG)


@bp.app_template_filter('price')
def get_price_display(price: int) -> str:
    neg = '-' if price < 0 else ''
    price = abs(price)
    yuan = price // 100
    fen = str(price % 100).zfill(2)
    return f'<span class="price"><span>¥</span>&nbsp;{neg}{yuan}.{fen}</span>'


@bp.app_template_filter('ts2dt')
def ts2dt(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


@bp.app_template_filter('date')
def dt2date(dt: datetime) -> str:
    return dt.strftime(r'%Y-%m-%d')


@bp.app_template_filter('datetime')
def dt2datetime(dt: datetime) -> str:
    return dt.strftime(r'%Y-%m-%d %H:%M:%S')

