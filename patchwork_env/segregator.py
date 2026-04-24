"""segregator.py – split env keys into 'public' and 'private' buckets.

Public keys are those whose values are safe to share (non-secret).
Private keys are those that look like secrets (passwords, tokens, etc.).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_SECRET_PATTERN = re.compile(
    r"(secret|password|passwd|token|api[_-]?key|private[_-]?key"
    r"|auth|credential|cert|passphrase|access[_-]?key|signing)",
    re.IGNORECASE,
)


def _is_private(key: str) -> bool:
    return bool(_SECRET_PATTERN.search(key))


@dataclass
class SegregateResult:
    public: Dict[str, str]
    private: Dict[str, str]
    all_keys: List[str] = field(default_factory=list)

    @property
    def public_count(self) -> int:
        return len(self.public)

    @property
    def private_count(self) -> int:
        return len(self.private)

    @property
    def total(self) -> int:
        return len(self.all_keys)

    def keys_in(self, bucket: str) -> List[str]:
        if bucket == "public":
            return sorted(self.public)
        if bucket == "private":
            return sorted(self.private)
        return []


def segregate_env(
    env: Dict[str, str],
    *,
    extra_private_patterns: List[str] | None = None,
) -> SegregateResult:
    """Segregate *env* into public and private buckets.

    Parameters
    ----------
    env:
        Parsed env dict.
    extra_private_patterns:
        Additional regex patterns (case-insensitive) to mark keys as private.
    """
    patterns = [_SECRET_PATTERN]
    if extra_private_patterns:
        for p in extra_private_patterns:
            patterns.append(re.compile(p, re.IGNORECASE))

    public: Dict[str, str] = {}
    private: Dict[str, str] = {}

    for key, value in env.items():
        if any(pat.search(key) for pat in patterns):
            private[key] = value
        else:
            public[key] = value

    return SegregateResult(
        public=public,
        private=private,
        all_keys=list(env.keys()),
    )
