from nacl.public import PrivateKey, PublicKey, SealedBox

from ..config import *
from ..secret import SECRET


def encrypt(msg: str) -> bytes:
    return SealedBox(PublicKey(SECRET)).encrypt(msg.encode())


def decrypt(cipher: bytes, skey: str) -> str:
    return SealedBox(PrivateKey(bytes.fromhex(skey))).decrypt(cipher).decode()
