import hashlib
import hmac
from time import time

from ..config import *
from ..secret import SECRET

SIG_LEN = hashlib.sha256().digest_size * 2


def sign_msg(typ: str, msg: str, valid_for: int = 60) -> str:
    expiry = (int(time()) + valid_for) if valid_for else 0
    token = f'{typ}:{msg}:{expiry}'
    sig = hmac.digest(SECRET, token.encode(), hashlib.sha256).hex()
    return f'{token}:{sig}'


def verify_msg(signed: str) -> tuple[str, str]:
    try:
        token, sig = signed[:-SIG_LEN-1], signed[-SIG_LEN:]
        expect = hmac.digest(SECRET, token.encode(), hashlib.sha256).hex()
        if not hmac.compare_digest(sig, expect):
            raise ValueError('bad signature')
        typ, *msg, expiry = token.split(':')
        if expiry != '0' and time() > int(expiry):
            raise ValueError('timestamp expired')
        return (typ, ':'.join(msg))
    except Exception:
        return ('', '')
