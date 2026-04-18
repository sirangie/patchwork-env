"""Redact secret values from an env dict before display or logging."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

_SECRET_PATTERNS = (
    "SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "APIKEY",
    "PRIVATE", "AUTH", "CREDENTIAL", "DSN", "DATABASE_URL",
)

DEFAULT_MASK = "***REDACTED***"


def _is_secret_key(key: str) -> bool:
    upper = key.upper()
    return any(pat in upper for pat in _SECRET_PATTERNS)


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str]

    @property
    def count(self) -> int:
        return len(self.redacted_keys)


def redact_env(
    env: Dict[str, str],
    mask: str = DEFAULT_MASK,
    extra_keys: Optional[List[str]] = None,
) -> RedactResult:
    """Return a copy of *env* with secret values replaced by *mask*."""
    extra = {k.upper() for k in (extra_keys or [])}
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_secret_key(key) or key.upper() in extra:
            redacted[key] = mask
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(original=env, redacted=redacted, redacted_keys=sorted(redacted_keys))
