"""sanitizer.py — strip or replace unsafe characters from env values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_NEWLINE_RE = re.compile(r"[\r\n]")


@dataclass
class SanitizeOp:
    key: str
    original: str
    sanitized: str
    reasons: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SanitizeOp({self.key!r}, changed={self.changed})"

    @property
    def changed(self) -> bool:
        return self.original != self.sanitized


@dataclass
class SanitizeResult:
    ops: List[SanitizeOp]
    env: Dict[str, str]

    @property
    def changed_count(self) -> int:
        return sum(1 for op in self.ops if op.changed)

    @property
    def unchanged_count(self) -> int:
        return sum(1 for op in self.ops if not op.changed)

    @property
    def changed_keys(self) -> List[str]:
        return [op.key for op in self.ops if op.changed]


def sanitize_env(
    env: Dict[str, str],
    *,
    strip_control: bool = True,
    collapse_newlines: bool = True,
    newline_replacement: str = " ",
    strip_surrounding_whitespace: bool = True,
    max_length: Optional[int] = None,
) -> SanitizeResult:
    """Return a sanitized copy of *env* and a log of every change made."""
    ops: List[SanitizeOp] = []
    out: Dict[str, str] = {}

    for key, value in env.items():
        reasons: List[str] = []
        result = value

        if strip_surrounding_whitespace and result != result.strip():
            result = result.strip()
            reasons.append("stripped surrounding whitespace")

        if strip_control and _CONTROL_RE.search(result):
            result = _CONTROL_RE.sub("", result)
            reasons.append("removed control characters")

        if collapse_newlines and _NEWLINE_RE.search(result):
            result = _NEWLINE_RE.sub(newline_replacement, result)
            reasons.append("collapsed newlines")

        if max_length is not None and len(result) > max_length:
            result = result[:max_length]
            reasons.append(f"truncated to {max_length} chars")

        ops.append(SanitizeOp(key=key, original=value, sanitized=result, reasons=reasons))
        out[key] = result

    return SanitizeResult(ops=ops, env=out)
