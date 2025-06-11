from collections import namedtuple

# SECRET is used for
# 1. Flask session signature  (HMAC-SHA1)
# 2. login ticket  signature  (HMAC-SHA256)
# 3. legal ID      encryption (Curve25519 Public)
#    SK = nacl.public.PrivateKey.generate()
#    SECRET = SK.public_key.encode().hex()
SECRET = bytes.fromhex('')

# Telegram Bot Token
BOT_TOKEN = ''

# Email SMTP
SMTP = namedtuple('SMTP', 'server,port,login,password')
EMAIL_PROVIDERS = {
    'txcloud': SMTP(
        'smtp.qcloudmail.com', 465,
        'noreply@aoscc.aosc.io', '',
    ),
    'mailgun': SMTP(
        'smtp.mailgun.org', 465,
        'noreply@aoscc.aosc.io', '',
    ),
}
