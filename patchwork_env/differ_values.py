"""Compare values for the same key across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValueDiffEntry:
    key: str
    values: Dict[str, Optional[str]]  # label -> value

    def __repr__(self) -> str:  # pragma: no cover
        return f"ValueDiffEntry(key={self.key!r}, values={self.values})"

    @property
    def is_consistent(self) -> bool:
        """True when all labels agree on the same value."""
        unique = set(v for v in self.values.values() if v is not None)
        return len(unique) <= 1

    @property
    def missing_in(self) -> List[str]:
        """Labels where the key is absent."""
        return [label for label, val in self.values.items() if val is None]


@dataclass
class ValueDiffResult:
    base_label: str
    target_labels: List[str]
    entries: List[ValueDiffEntry] = field(default_factory=list)

    @property
    def all_labels(self) -> List[str]:
        return [self.base_label] + self.target_labels

    @property
    def inconsistent(self) -> List[ValueDiffEntry]:
        return [e for e in self.entries if not e.is_consistent]

    @property
    def consistent(self) -> List[ValueDiffEntry]:
        return [e for e in self.entries if e.is_consistent]

    @property
    def has_differences(self) -> bool:
        return len(self.inconsistent) > 0

    def for_key(self, key: str) -> Optional[ValueDiffEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def diff_values(
    base_env: Dict[str, str],
    base_label: str,
    targets: List[Dict[str, str]],
    target_labels: List[str],
) -> ValueDiffResult:
    """Compare values for shared keys across base and target envs."""
    if len(targets) != len(target_labels):
        raise ValueError("targets and target_labels must have the same length")

    all_keys: List[str] = list(
        dict.fromkeys(
            list(base_env.keys()) + [k for env in targets for k in env.keys()]
        )
    )

    entries: List[ValueDiffEntry] = []
    for key in all_keys:
        values: Dict[str, Optional[str]] = {base_label: base_env.get(key)}
        for label, env in zip(target_labels, targets):
            values[label] = env.get(key)
        entries.append(ValueDiffEntry(key=key, values=values))

    return ValueDiffResult(
        base_label=base_label,
        target_labels=target_labels,
        entries=entries,
    )
