"""Flatten nested or prefixed env keys into a single-level dict with optional separator replacement."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenOp:
    original_key: str
    flat_key: str
    value: str
    changed: bool

    def __repr__(self) -> str:
        arrow = f"{self.original_key} -> {self.flat_key}" if self.changed else self.original_key
        return f"FlattenOp({arrow}={self.value!r})"


@dataclass
class FlattenResult:
    ops: List[FlattenOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def changed_count(self) -> int:
        return sum(1 for op in self.ops if op.changed)

    @property
    def unchanged_count(self) -> int:
        return sum(1 for op in self.ops if not op.changed)

    @property
    def renamed_keys(self) -> List[str]:
        return [op.original_key for op in self.ops if op.changed]


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    replacement: str = "_",
    uppercase: bool = True,
) -> FlattenResult:
    """Replace separator sequences in keys and optionally uppercase them.

    Args:
        env: source key/value pairs
        separator: substring in keys to replace (default ``__``)
        replacement: what to replace it with (default ``_``)
        uppercase: if True, keys are uppercased after replacement
    """
    ops: List[FlattenOp] = []
    out: Dict[str, str] = {}

    for key, value in env.items():
        flat = key.replace(separator, replacement)
        if uppercase:
            flat = flat.upper()
        changed = flat != key
        ops.append(FlattenOp(original_key=key, flat_key=flat, value=value, changed=changed))
        out[flat] = value

    return FlattenResult(ops=ops, env=out)
