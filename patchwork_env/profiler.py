"""Profile an env file: count keys, detect secrets, check for empties."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_SECRET_HINTS = (
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "private", "auth", "credential", "cert", "key",
)


@dataclass
class ProfileResult:
    total: int = 0
    empty: List[str] = field(default_factory=list)
    likely_secrets: List[str] = field(default_factory=list)
    safe: List[str] = field(default_factory=list)

    @property
    def empty_count(self) -> int:
        return len(self.empty)

    @property
    def secret_count(self) -> int:
        return len(self.likely_secrets)

    @property
    def safe_count(self) -> int:
        return len(self.safe)


def _is_likely_secret(key: str) -> bool:
    lower = key.lower()
    return any(hint in lower for hint in _SECRET_HINTS)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse a parsed env dict and return a ProfileResult."""
    result = ProfileResult(total=len(env))
    for key, value in env.items():
        if value == "":
            result.empty.append(key)
        elif _is_likely_secret(key):
            result.likely_secrets.append(key)
        else:
            result.safe.append(key)
    result.empty.sort()
    result.likely_secrets.sort()
    result.safe.sort()
    return result
