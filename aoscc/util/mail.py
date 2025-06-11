import re
import smtplib
from time import time
from html import escape
from collections import defaultdict
from email.mime.text import MIMEText
from email.utils import make_msgid

from flask import request

from ..config import *
from ..secret import EMAIL_PROVIDERS
from .verify import sign_msg
from .tg import send_telegram


def send_email(email: str, title: str, msg: str) -> str:
    try:
        host = email.split('@')[1]
        smtp_provider = EMAIL_PROVIDERS[DEFAULT_PROVIDER]
        for pattern, provider in EMAIL_RULES:
            if re.match(pattern, host):
                smtp_provider = EMAIL_PROVIDERS[provider]
        message = MIMEText(msg)
        msgid = make_msgid(domain=smtp_provider.login.split('@')[1])
        message['Message-ID'] = msgid
        message['From'] = MAIL_FROM
        message['Reply-To'] = MAIL_REPLY_TO
        message['To'] = email
        message['Subject'] = title
        with smtplib.SMTP_SSL(smtp_provider.server, smtp_provider.port) as server:
            server.login(smtp_provider.login, smtp_provider.password)
            server.sendmail(smtp_provider.login, [email], message.as_string())
        return f'via {smtp_provider.server} msgid {msgid}'
    except Exception as exc:
        send_telegram(LOG_ID, repr(exc))
        return ''


class TokenBucket:
    def __init__(self, size: int=1, rate_per_sec: float=0.0):
        self.size = float(size)
        self.rate = float(rate_per_sec)
        self.x = float(size)
        self.last = time()
    def __call__(self) -> bool:
        self.x = min(self.size, self.x + self.rate * (time()-self.last))
        self.last = time()
        if self.x >= 1:
            self.x -= 1
            return True
        else:
            return False


global_bucket = TokenBucket(*GLOBAL_LIMIT)
perip_buckets = defaultdict(lambda: TokenBucket(*PERIP_LIMIT))


def send_email_login(email: str) -> str:
    if email == 'example@aosc.io':
        return '不要输入示例地址呀...'
    addr = request.remote_addr
    if not global_bucket() or not perip_buckets[addr]():
        send_telegram(LOG_ID, f'#REJECTED {addr} {email}')
        return '发送验证邮件频率过高，请稍后再试。'
    msg = f"""您好，

欢迎注册 {TITLE} ！请点击以下链接登入会议注册系统，链接有效期 {LOGIN_TOKEN_EXPIRY} 分钟。

{URL_BASE}/login/{sign_msg('email', email, LOGIN_TOKEN_EXPIRY*60)}

请勿回复此邮件，如需更多协助，请联系 aoscc@aosc.io 。
"""
    if result := send_email(email, f'欢迎您注册 {TITLE} ！', msg):
        send_telegram(LOG_ID, f'#SENT {addr} {email} {escape(result)}')
        return '验证邮件已发送到您的邮箱，请注意查收，并记得检查垃圾邮件箱。如果没有收到，请十分钟后再试。'
    else:
        send_telegram(LOG_ID, f'#FAILED {addr} {email}')
        return '发送时遇到错误。'
