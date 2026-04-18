"""Filter .env entries by key pattern or value presence."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str]
    excluded: Dict[str, str]

    @property
    def count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)


def filter_env(
    env: Dict[str, str],
    pattern: Optional[str] = None,
    exclude_empty: bool = False,
    keys: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Return entries matching the given criteria.

    Args:
        env: parsed env dict
        pattern: regex applied to key names
        exclude_empty: drop keys whose value is empty string
        keys: explicit allowlist of keys to keep
        invert: flip the match — keep what would have been excluded
    """
    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    compiled = re.compile(pattern) if pattern else None

    for k, v in env.items():
        keep = True

        if compiled and not compiled.search(k):
            keep = False
        if exclude_empty and v == "":
            keep = False
        if keys is not None and k not in keys:
            keep = False

        if invert:
            keep = not keep

        if keep:
            matched[k] = v
        else:
            excluded[k] = v

    return FilterResult(matched=matched, excluded=excluded)
