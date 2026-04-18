"""Simple symmetric encryption helpers for masking secret values at rest."""

import base64
import hashlib
import os
from typing import Dict

_MARKER = "enc:"


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def encrypt_value(value: str, passphrase: str) -> str:
    """XOR-encrypt a value and return a base64-encoded string prefixed with enc:."""
    key = _derive_key(passphrase)
    salt = os.urandom(16)
    key_stream = (key * ((len(value) // 32) + 2))[: len(value)]
    encrypted = bytes(b ^ k for b, k in zip(value.encode(), key_stream))
    payload = salt + encrypted
    return _MARKER + base64.urlsafe_b64encode(payload).decode()


def decrypt_value(token: str, passphrase: str) -> str:
    """Decrypt a value produced by encrypt_value."""
    if not token.startswith(_MARKER):
        raise ValueError(f"Not an encrypted token: {token!r}")
    payload = base64.urlsafe_b64decode(token[len(_MARKER):])
    salt = payload[:16]  # noqa: F841 — reserved for future KDF use
    encrypted = payload[16:]
    key = _derive_key(passphrase)
    key_stream = (key * ((len(encrypted) // 32) + 2))[: len(encrypted)]
    decrypted = bytes(b ^ k for b, k in zip(encrypted, key_stream))
    return decrypted.decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(_MARKER)


def encrypt_env(env: Dict[str, str], passphrase: str, keys: list[str] | None = None) -> Dict[str, str]:
    """Return a new env dict with specified keys (or all) encrypted."""
    result = {}
    for k, v in env.items():
        if (keys is None or k in keys) and not is_encrypted(v):
            result[k] = encrypt_value(v, passphrase)
        else:
            result[k] = v
    return result


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a new env dict with all encrypted values decrypted."""
    return {
        k: (decrypt_value(v, passphrase) if is_encrypted(v) else v)
        for k, v in env.items()
    }
