"""Deduplicator: remove duplicate keys from an env dict, keeping first or last occurrence."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal


@dataclass
class DedupeOp:
    key: str
    kept_value: str
    dropped_values: List[str]
    strategy: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"DedupeOp({self.key!r}, kept={self.kept_value!r}, dropped={self.dropped_values})"


@dataclass
class DedupeResult:
    env: Dict[str, str]
    ops: List[DedupeOp] = field(default_factory=list)

    @property
    def deduplicated_count(self) -> int:
        return len(self.ops)

    @property
    def clean(self) -> bool:
        return self.deduplicated_count == 0

    @property
    def deduplicated_keys(self) -> List[str]:
        return [op.key for op in self.ops]


def deduplicate_env(
    raw_pairs: List[tuple],
    strategy: Literal["first", "last"] = "last",
) -> DedupeResult:
    """Given a list of (key, value) pairs (possibly with repeated keys),
    return a DedupeResult with duplicates resolved per *strategy*.

    'first' keeps the first occurrence; 'last' keeps the last.
    """
    seen: Dict[str, List[str]] = {}
    order: List[str] = []

    for key, value in raw_pairs:
        if key not in seen:
            seen[key] = []
            order.append(key)
        seen[key].append(value)

    ops: List[DedupeOp] = []
    env: Dict[str, str] = {}

    for key in order:
        values = seen[key]
        if len(values) == 1:
            env[key] = values[0]
            continue

        if strategy == "first":
            kept = values[0]
            dropped = values[1:]
        else:
            kept = values[-1]
            dropped = values[:-1]

        env[key] = kept
        ops.append(DedupeOp(key=key, kept_value=kept, dropped_values=dropped, strategy=strategy))

    return DedupeResult(env=env, ops=ops)
