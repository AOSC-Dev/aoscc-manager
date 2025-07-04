import re
from datetime import date, datetime, timedelta
from collections import namedtuple
NOW = datetime.now
ONE_DAY = timedelta(days=1)
FAR_FUTURE = datetime(2100, 1, 1, 0, 0, 0)

## basic info
TITLE = 'AOSCC 2025'
URL_BASE = 'https://aoscc.aosc.io'
MAX_FILE_SIZE = 10*1024*1024  # 10 MiB
SESSION_EXPIRY = timedelta(days=14)
LOGIN_TOKEN_EXPIRY = 20  # minutes
# see SECRET in secret.py

## telegram bot
# see BOT_TOKEN in secret.py
# forward questions to
MGMT_ID = -1002609311064
# runtime error report
LOG_ID = 263344415

## email
# see EMAIL_PROVIDERS in secret.py
MAIL_LOG_ID = -1002400222732
DEFAULT_PROVIDER = 'mailgun'
EMAIL_RULES = [
    (r'^((vip.)?qq|163|126|sina|foxmail)\.com$', 'txcloud'),
    (r'^.+\.cn$', 'txcloud'),
    (r'^(outlook|hotmail)\.[a-z]+$', 'txcloud'),
    (r'^(gmail|icloud)\.com$', 'mailgun'),
    (r'^(protonmail\.(com|ch)|(proton|pm)\.me)$', 'mailgun'),
    (r'^aosc\.io$', 'mailgun'),
]
MAIL_FROM = f'{TITLE} <noreply@aoscc.aosc.io>'
MAIL_REPLY_TO = f'{TITLE} <aoscc@aosc.io>'
# token bucket for email
GLOBAL_LIMIT = (100, 50/60/60)
PERIP_LIMIT = (2, 6/60/60)

## services
REGISTER_OPEN = False
REGISTER_SOFT = datetime(2025, 7, 15, 21, 0, 0)
BADGE_CLOSE = datetime(2025, 7, 15, 21, 0, 0)
ACCOMMO_CLOSE = datetime(2025, 7, 22, 12, 0, 0)
Room = namedtuple('Room', 'name,nguest,price,vacancy')
ROOM_OFFERING = {x.name: x for x in [
    Room('标准间', 2, 28000, 30),
    Room('大床房', 1, 28000, 10),
]}
DATE_RANGE = (date(2025, 7, 25), date(2025, 7, 27))
VOLUNTEER_OPEN = 'True'
VOLUNTEER_TSHIRT_SKU = tuple('S,M,L,XL,2XL,3XL,4XL,5XL'.split(','))

## merch
Item = namedtuple('Item', 'name,desc,img,sku,price,cutoff')
_tshirt_size = '，尺码表见<a href="https://www.tshe.com/items/youth108" target="_blank">此处</a>。' \
               '<br><br><b style="outline: 1px solid; padding: 1px">订购将于 7 月 4 日中午 12 时截止！</b>'
_tshirt_zhipen = '<br><br>使用<a href="javascript:alert(\'相较之前热转印烫画工艺，透气性及耐用度显著提升，浅色衣服透气性更佳。\')">数码直喷印制</a>'
_tshirt_siyin = '<br><br>使用<a href="javascript:alert(\'颜色清晰艳丽且较为透气，多次洗濯均不易掉色。\')">丝网染印</a>'
_tshirt_sku = {size: 9999 for size in 'S,M,L,XL,2XL,3XL,4XL'.split(',')}
_tshirt_cutoff = datetime(2025, 7, 4, 12, 0, 0)
_retros = ('美商先进牌 9950 型','松山湖 920 型','西安 612 型','Santa Clara 14900 型','常熟 1901 甲型','国际商贸牌力量 11 型','星际牌 K1 型','电计算 103 型')
INVENTORY = {x.name: x for x in [
    Item(
        'AOSCC 十周年 T 恤',
        '自 2015 年以来，AOSCC 已经在大家的陪伴下走过了 10 个年头。我们将往年 AOSCC 及校园行活动的剪影与安同开源社区徽标结合，推出了这款纪念 T 恤。'+_tshirt_zhipen+_tshirt_size,
        'tshirt/aoscc-10th.png',
        _tshirt_sku, 6200, _tshirt_cutoff,
    ),
    Item(
        '《安啦！》T 恤',
        '遇事学安安，安然如泰山！去年点着的软件工程之火今年也还没熄灭呢…… 那就让它接着烧吧，安啦！'+_tshirt_zhipen+_tshirt_size,
        'tshirt/anan-calm.png',
        _tshirt_sku, 5700, _tshirt_cutoff,
    ),
    Item(
        '《安安惊恐.webp》T 恤（黑）',
        'oma 乃是系统必备组件…… 喂！oma 1.17 发布贺图中的安安惊恐表情还在各群组传播，和大家一块 Σ(°△°ꪱꪱꪱ) 起来吧～ '+_tshirt_siyin+_tshirt_size,
        'tshirt/anan-panic-dark.png',
        _tshirt_sku, 5200, _tshirt_cutoff,
    ),
    Item(
        '《安安惊恐.webp》T 恤（米白）',
        'oma 乃是系统必备组件…… 喂！这件 T 恤也提供浅色版本哦～'+_tshirt_siyin+_tshirt_size,
        'tshirt/anan-panic-light.png',
        _tshirt_sku, 6500, _tshirt_cutoff,
    ),
    Item(
        '安安 Minecraft 印象 T 恤',
        '*hrrrn* *发出村民的声音* ，是先造火柴盒还是先修包呢？我们以 @安慕希 为安安设计的 Minecraft 人物模型为主题推出了这款 T 恤，安安 & MC 双厨狂喜！'+_tshirt_zhipen+_tshirt_size,
        'tshirt/anan-minecraft.png',
        _tshirt_sku, 6200, _tshirt_cutoff,
    ),
    Item(
        '复古处理器铭牌机箱贴',
        '我们为安同 OS 支持的 6 个处理器架构挑出了几款具有代表性（梗属性）的硬件制作了复古铭牌。<br><br>由于开模价格较高，我们选定其中三款制作了磁性冰箱贴，也可以用作机箱贴。<br><br>每款限量 50 个。',
        'retro-magnet.png',
        {x: 50 for x in _retros[:3]}, 1800, FAR_FUTURE,
    ),
    Item(
        '复古处理器铭牌钥匙扣',
        '我们为安同 OS 支持的 6 个处理器架构挑出了几款具有代表性（梗属性）的硬件制作了复古铭牌钥匙扣。<br><br>订购将于 7 月 10 日中午 12 时截止。',
        'retro-keychain.png',
        {x: 9999 for x in _retros}, 235, datetime(2025, 7, 10, 12, 0, 0),
    ),
    Item(
        '安安 Fumo 玩偶',
        '由社区好友 LiarOnce 委托“番茄炒蛋”社团画师 Yukata 设计的安安 Fumo 布偶，总算开始量产，走入本次元了！安安笑嘻嘻，电脑哭唧唧，快抱一只回家辟邪吧～<br><br>限量 20 个。',
        'anan-fumo.png',
        {'': 20}, 13000, FAR_FUTURE,
    ),
]}



ALL_CONFIG = {k: v for k, v in locals().items() if re.fullmatch(r'[A-Z]+(_[A-Z]+)*', k)}
__all__ = list(ALL_CONFIG.keys())+['ALL_CONFIG']
