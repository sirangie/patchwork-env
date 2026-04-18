"""Diff logic for comparing two .env file dictionaries."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    left_value: Optional[str] = None
    right_value: Optional[str] = None

    def __repr__(self):
        if self.status == 'added':
            return f"+ {self.key}={self.right_value}"
        elif self.status == 'removed':
            return f"- {self.key}={self.left_value}"
        elif self.status == 'changed':
            return f"~ {self.key}: {self.left_value!r} -> {self.right_value!r}"
        return f"  {self.key}={self.left_value}"


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    mask_values: bool = False,
) -> list[DiffEntry]:
    """Compare two env dicts and return a list of DiffEntry results."""
    entries = []
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        lv = _maybe_mask(left.get(key), mask_values)
        rv = _maybe_mask(right.get(key), mask_values)

        if in_left and not in_right:
            entries.append(DiffEntry(key, 'removed', left_value=lv))
        elif in_right and not in_left:
            entries.append(DiffEntry(key, 'added', right_value=rv))
        elif left[key] != right[key]:
            entries.append(DiffEntry(key, 'changed', left_value=lv, right_value=rv))
        else:
            entries.append(DiffEntry(key, 'unchanged', left_value=lv, right_value=rv))

    return entries


def _maybe_mask(value: Optional[str], mask: bool) -> Optional[str]:
    if value is None:
        return None
    return '***' if mask else value


def summary(entries: list[DiffEntry]) -> Dict[str, int]:
    counts: Dict[str, int] = {'added': 0, 'removed': 0, 'changed': 0, 'unchanged': 0}
    for e in entries:
        counts[e.status] += 1
    return counts
