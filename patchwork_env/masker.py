"""masker.py — Selectively mask env values based on key patterns or an allowlist."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_DEFAULT_PATTERNS = [
    r"(?i)(secret|password|passwd|token|api_?key|private|credential|auth)"
]

PLACEHOLDER = "***"


@dataclass
class MaskOp:
    key: str
    original: str
    masked: bool
    reason: str = ""

    def __repr__(self) -> str:
        tag = "MASKED" if self.masked else "kept"
        return f"MaskOp({self.key!r}, {tag})"


@dataclass
class MaskResult:
    ops: List[MaskOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def masked_count(self) -> int:
        return sum(1 for o in self.ops if o.masked)

    @property
    def kept_count(self) -> int:
        return sum(1 for o in self.ops if not o.masked)

    @property
    def masked_keys(self) -> List[str]:
        return [o.key for o in self.ops if o.masked]


def _matches_any(key: str, patterns: List[str]) -> bool:
    return any(re.search(p, key) for p in patterns)


def mask_env(
    env: Dict[str, str],
    *,
    patterns: Optional[List[str]] = None,
    allowlist: Optional[List[str]] = None,
    placeholder: str = PLACEHOLDER,
    mask_empty: bool = False,
) -> MaskResult:
    """Return a MaskResult where secret-looking keys are replaced with placeholder."""
    pats = patterns if patterns is not None else _DEFAULT_PATTERNS
    allow = set(allowlist or [])
    result = MaskResult()

    for key, value in env.items():
        if key in allow:
            op = MaskOp(key=key, original=value, masked=False, reason="allowlisted")
            result.env[key] = value
        elif not value and not mask_empty:
            op = MaskOp(key=key, original=value, masked=False, reason="empty")
            result.env[key] = value
        elif _matches_any(key, pats):
            op = MaskOp(key=key, original=value, masked=True, reason="pattern match")
            result.env[key] = placeholder
        else:
            op = MaskOp(key=key, original=value, masked=False, reason="")
            result.env[key] = value
        result.ops.append(op)

    return result
