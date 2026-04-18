"""Sort .env keys alphabetically or by custom group order."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    env: Dict[str, str]
    original_order: List[str]
    sorted_order: List[str]
    groups: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def moved(self) -> int:
        return sum(
            1 for i, (a, b) in enumerate(zip(self.original_order, self.sorted_order)) if a != b
        )


def sort_env(
    env: Dict[str, str],
    *,
    reverse: bool = False,
    group_prefixes: Optional[List[str]] = None,
) -> SortResult:
    """Return a SortResult with keys sorted alphabetically.

    If group_prefixes is provided, keys matching each prefix are grouped
    together (in prefix order) before the remaining keys.
    """
    original_order = list(env.keys())

    if group_prefixes:
        groups: Dict[str, List[str]] = {p: [] for p in group_prefixes}
        remainder: List[str] = []
        for key in original_order:
            matched = False
            for prefix in group_prefixes:
                if key.startswith(prefix):
                    groups[prefix].append(key)
                    matched = True
                    break
            if not matched:
                remainder.append(key)

        for g in groups.values():
            g.sort(reverse=reverse)
        remainder.sort(reverse=reverse)

        sorted_order = [k for p in group_prefixes for k in groups[p]] + remainder
    else:
        groups = {}
        sorted_order = sorted(original_order, reverse=reverse)

    sorted_env = {k: env[k] for k in sorted_order}
    return SortResult(
        env=sorted_env,
        original_order=original_order,
        sorted_order=sorted_order,
        groups=groups,
    )
