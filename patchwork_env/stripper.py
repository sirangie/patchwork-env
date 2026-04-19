"""stripper.py — remove keys matching a pattern or list from an env dict."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class StripOp:
    key: str
    value: str
    reason: str  # 'pattern' | 'explicit'

    def __repr__(self) -> str:
        return f"StripOp({self.key!r}, reason={self.reason!r})"


@dataclass
class StripResult:
    original: Dict[str, str]
    stripped: Dict[str, str]
    ops: List[StripOp] = field(default_factory=list)

    @property
    def removed_count(self) -> int:
        return len(self.ops)

    @property
    def removed_keys(self) -> List[str]:
        return [op.key for op in self.ops]


def strip_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
) -> StripResult:
    """Return a new env with matching keys removed."""
    keys = keys or []
    explicit = set(keys)
    regex = re.compile(pattern) if pattern else None

    ops: List[StripOp] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        if k in explicit:
            ops.append(StripOp(key=k, value=v, reason="explicit"))
        elif regex and regex.search(k):
            ops.append(StripOp(key=k, value=v, reason="pattern"))
        else:
            result[k] = v

    return StripResult(original=dict(env), stripped=result, ops=ops)
