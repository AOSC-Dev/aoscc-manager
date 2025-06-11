import re
from datetime import date, datetime, timedelta
from collections import namedtuple

## basic info
TITLE = 'AOSCC 2025'
TESTING = False
URL_BASE = 'https://aoscc.aosc.io'
MAX_FILE_SIZE = 10*1024*1024  # 10 MiB
SESSION_EXPIRY = timedelta(days=14)
LOGIN_TOKEN_EXPIRY = 20  # minutes

## telegram bot
# forward questions to
MGMT_ID = -1002609311064
# used in URL of login message
LOG_ID = -1002400222732

## email
# SMTP credentials
SMTP_SERVER = 'smtp.qcloudmail.com'
SMTP_PORT = 465
SMTP_USERNAME = 'noreply@aoscc.aosc.io'
MAIL_FROM = f'{TITLE} <{SMTP_USERNAME}>'
MAIL_REPLY_TO = f'{TITLE} <aoscc@aosc.io>'
# token bucket for email
GLOBAL_LIMIT = (100, 50/60/60)
PERIP_LIMIT = (2, 6/60/60)

## services
REGISTER_CLOSE = datetime(2025, 7, 15, 21, 0, 0)
BADGE_CLOSE = datetime(2025, 7, 15, 21, 0, 0)
ACCOMMO_CLOSE = datetime(2025, 7, 22, 12, 0, 0)
Room = namedtuple('Room', 'name,nguest,price,vacancy')
ROOM_OFFERING = {x.name: x for x in [
    Room('标准间', 2, 28000, 35),
    Room('大床房', 1, 28000, 5),
]}
DATE_RANGE = (date(2025, 7, 25), date(2025, 7, 27))
VOLUNTEER_OPEN = True
VOLUNTEER_TSHIRT_SKU = tuple('S,M,L,XL,2XL,3XL,4XL,5XL'.split(','))

## merch
MERCH_OPEN = datetime(2025, 6, 7, 22, 0, 0)
MERCH_CLOSE = datetime(2025, 7, 4, 0, 0, 0)
# inventory
Item = namedtuple('Item', 'name,desc,img,sku,price')
_tshirt_size = '，尺码表见<a href="https://www.tshe.com/items/youth108" target="_blank">此处</a>。'
_tshirt_zhipen = '使用<a href="javascript:alert(\'相较之前热转印烫画工艺，透气性及耐用度显著提升，浅色衣服透气性更佳。\')">数码直喷印制</a>'
_tshirt_siyin = '使用<a href="javascript:alert(\'颜色清晰艳丽且较为透气，多次洗濯均不易掉色。\')">丝网染印</a>'
_tshirt_sku = tuple('S,M,L,XL,2XL,3XL,4XL'.split(','))
INVENTORY = {x.name: x for x in [
    Item(
        '《安啦》T 恤',
        _tshirt_zhipen+_tshirt_size,
        'tshirt25/anan-calm.png',
        _tshirt_sku, 5700,
    ),
    Item(
        'AOSCC 十周年 T 恤',
        _tshirt_zhipen+_tshirt_size,
        'tshirt25/aoscc-10th.png',
        _tshirt_sku, 6200
    ),
    Item(
        '《安安害怕》T 恤（黑）',
        _tshirt_siyin+_tshirt_size,
        'tshirt25/anan-panic-dark.png',
        _tshirt_sku, 5200
    ),
    Item(
        '《安安害怕》T 恤（米白）',
        _tshirt_siyin+_tshirt_size,
        'tshirt25/anan-panic-light.png',
        _tshirt_sku, 6500
    ),
    Item(
        '安安 Minecraft 印象 T 恤',
        _tshirt_zhipen+_tshirt_size,
        'tshirt25/anan-minecraft.png',
        _tshirt_sku, 6200
    ),
]}

NOW = datetime.now
ONE_DAY = timedelta(days=1)


ALL_CONFIG = {k: v for k, v in locals().items() if re.fullmatch(r'[A-Z]+(_[A-Z]+)*', k)}
__all__ = list(ALL_CONFIG.keys())+['ALL_CONFIG']
