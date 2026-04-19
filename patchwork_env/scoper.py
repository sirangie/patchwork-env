"""Scope filtering: restrict env keys to a named scope prefix or tag set."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope: str
    env: Dict[str, str]
    included: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.included) + len(self.excluded)

    @property
    def included_count(self) -> int:
        return len(self.included)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)


def scope_env(
    env: Dict[str, str],
    scope: str,
    *,
    strip_prefix: bool = False,
    case_sensitive: bool = False,
) -> ScopeResult:
    """Return only keys matching *scope* as a prefix (e.g. 'DB' matches 'DB_HOST')."""
    prefix = scope if case_sensitive else scope.upper()
    included: List[str] = []
    excluded: List[str] = []
    scoped: Dict[str, str] = {}

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        needle = prefix + "_"
        if compare_key == prefix or compare_key.startswith(needle):
            included.append(key)
            out_key = key
            if strip_prefix:
                # remove the leading scope prefix and underscore
                out_key = key[len(scope) + 1:] if len(key) > len(scope) else key
            scoped[out_key] = value
        else:
            excluded.append(key)

    return ScopeResult(scope=scope, env=scoped, included=included, excluded=excluded)
