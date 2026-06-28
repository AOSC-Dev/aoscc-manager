import re
from datetime import datetime, timedelta
NOW = datetime.now

## basic info
TITLE = 'AOSCC 2026'
URL_BASE = 'https://aoscc.aosc.io'
MAX_FILE_SIZE = 10*1024*1024  # 10 MiB
SESSION_EXPIRY = timedelta(days=14)
LOGIN_TOKEN_EXPIRY = 20  # minutes
AUTO_ADMIN = [
    ('telegram', '263344415', ('admin',)),
    ('email', 'jeffbai@aosc.io', ('admin',)),
]
# see SECRET in secret.py

## telegram bot
# see BOT_TOKEN in secret.py
# forward questions to
PRIVATE_QUESTION_ID = -1002609311064
# runtime error report
REPORTING_ID = 263344415
# contributor group id
BAKA_GROUP_ID = -1001109254909
# email sending log
MAIL_LOG_ID = -1002400222732

## email
# see EMAIL_PROVIDERS in secret.py
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

## register
REGISTER_OPEN = True
INTERNAL_ONLY = True
REGISTER_CAP = 160
RESERVE_CUTOFF = datetime(2026, 7, 31, 23, 59, 59)
REGISTER_CUTOFF = datetime(2026, 8, 7, 23, 59, 59)

## services
BADGE_CUTOFF = datetime(2026, 8, 7, 23, 59, 59)
VOLUNTEER_OPEN = True

ALL_CONFIG = {k: v for k, v in locals().items() if re.fullmatch(r'[A-Z]+(_[A-Z]+)*', k)}
__all__ = list(ALL_CONFIG.keys())+['ALL_CONFIG']
