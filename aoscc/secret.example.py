# SECRET is used for
# 1. Flask session signature  (HMAC-SHA1)
# 2. login ticket  signature  (HMAC-SHA256)
# 3. legal ID      encryption (Curve25519 Public)
#    SK = nacl.public.PrivateKey.generate()
#    SECRET = SK.public_key.encode().hex()
SECRET = bytes.fromhex('')

# Telegram Bot Token
BOT_TOKEN = ''

# Email SMTP Password
SMTP_PASSWORD = ''
