import hashlib
import hmac
from time import time

from nacl.public import PrivateKey, PublicKey, SealedBox

from ..config import *
from ..secret import SECRET


def encrypt(msg: str) -> bytes:
    return SealedBox(PublicKey(SECRET)).encrypt(msg.encode())


def decrypt(cipher: bytes, skey: str) -> str:
    return SealedBox(PrivateKey(bytes.fromhex(skey))).decrypt(cipher).decode()


def sign_msg(typ: str, msg: str, valid_for: int = 60) -> str:
    expiry = (int(time()) + valid_for) if valid_for else 0
    token = f'{typ}:{msg}:{expiry}'
    sig = hmac.digest(SECRET, token.encode(), hashlib.sha256).hex()[0:32]
    return f'{token}:{sig}'


def verify_msg(signed: str) -> tuple[str, str]:
    try:
        token, sig = signed[:-32-1], signed[-32:]
        expect = hmac.digest(SECRET, token.encode(), hashlib.sha256).hex()[0:32]
        if not hmac.compare_digest(sig, expect):
            raise ValueError('bad signature')
        typ, *msg, expiry = token.split(':')
        if expiry != '0' and time() > int(expiry):
            raise ValueError('timestamp expired')
        return (typ, ':'.join(msg))
    except Exception:
        return ('', '')
