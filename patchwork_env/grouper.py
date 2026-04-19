"""Group .env keys by prefix (e.g. DB_, AWS_, APP_)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]
    separator: str = "_"

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_keys(self) -> int:
        total = sum(len(v) for v in self.groups.values())
        return total + len(self.ungrouped)

    def keys_in(self, group: str) -> List[str]:
        return sorted(self.groups.get(group, {}).keys())


def group_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
    min_prefix_len: int = 2,
) -> GroupResult:
    """Group keys by common prefix.

    If *prefixes* is given, only those prefixes are used.
    Otherwise prefixes are inferred from the keys themselves.
    """
    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    if prefixes is None:
        # infer prefixes: take the part before the first separator
        inferred: Dict[str, int] = {}
        for key in env:
            if separator in key:
                prefix = key.split(separator, 1)[0]
                if len(prefix) >= min_prefix_len:
                    inferred[prefix] = inferred.get(prefix, 0) + 1
        # only keep prefixes that appear more than once
        prefixes = [p for p, count in inferred.items() if count > 1]

    prefix_set = set(prefixes)

    for key, value in env.items():
        matched = False
        if separator in key:
            prefix = key.split(separator, 1)[0]
            if prefix in prefix_set:
                groups.setdefault(prefix, {})[key] = value
                matched = True
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped, separator=separator)
