import os

from cryptography.fernet import Fernet

_KEY_FILE = "mirror.key"


def _load_key():
    env_key = os.getenv("MIRROR_ENCRYPTION_KEY")
    if env_key:
        return env_key.encode()

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read()

    key = Fernet.generate_key()
    with open(_KEY_FILE, "wb") as f:
        f.write(key)
    return key


_fernet = Fernet(_load_key())


def encrypt_token(token: str) -> bytes:
    return _fernet.encrypt(token.encode())


def decrypt_token(data: bytes) -> str:
    return _fernet.decrypt(data).decode()
