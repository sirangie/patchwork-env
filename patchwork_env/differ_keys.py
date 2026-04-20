"""Key-set differ: compare which keys exist across two envs, ignoring values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class KeyDiffResult:
    base_label: str
    target_label: str
    base_keys: Set[str]
    target_keys: Set[str]
    only_in_base: List[str] = field(default_factory=list)
    only_in_target: List[str] = field(default_factory=list)
    shared: List[str] = field(default_factory=list)

    @property
    def total_unique(self) -> int:
        return len(self.base_keys | self.target_keys)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_base or self.only_in_target)

    @property
    def coverage(self) -> float:
        """Fraction of total unique keys present in both envs."""
        total = self.total_unique
        return len(self.shared) / total if total else 1.0


def diff_keys(
    base: Dict[str, str],
    target: Dict[str, str],
    base_label: str = "base",
    target_label: str = "target",
) -> KeyDiffResult:
    """Return a KeyDiffResult describing key-set differences between two envs."""
    base_keys: Set[str] = set(base)
    target_keys: Set[str] = set(target)

    only_in_base = sorted(base_keys - target_keys)
    only_in_target = sorted(target_keys - base_keys)
    shared = sorted(base_keys & target_keys)

    return KeyDiffResult(
        base_label=base_label,
        target_label=target_label,
        base_keys=base_keys,
        target_keys=target_keys,
        only_in_base=only_in_base,
        only_in_target=only_in_target,
        shared=shared,
    )
