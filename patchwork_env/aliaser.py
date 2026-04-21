"""aliaser.py – rename keys via an alias map without losing original values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasOp:
    original_key: str
    alias_key: str
    value: str
    skipped: bool = False
    reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        tag = f"SKIP({self.reason})" if self.skipped else "OK"
        return f"AliasOp({self.original_key} -> {self.alias_key}, {tag})"


@dataclass
class AliasResult:
    ops: List[AliasOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def aliased_count(self) -> int:
        return sum(1 for op in self.ops if not op.skipped)

    @property
    def skipped_count(self) -> int:
        return sum(1 for op in self.ops if op.skipped)

    @property
    def aliased_keys(self) -> List[str]:
        return [op.alias_key for op in self.ops if not op.skipped]


def alias_env(
    env: Dict[str, str],
    alias_map: Dict[str, str],
    keep_original: bool = False,
    overwrite: bool = False,
) -> AliasResult:
    """Apply *alias_map* (original_key -> alias_key) to *env*.

    Args:
        env: source environment dict.
        alias_map: mapping of existing key names to their desired alias.
        keep_original: when True the original key is retained alongside the alias.
        overwrite: when True an existing alias key is overwritten; otherwise skipped.
    """
    result_env: Dict[str, str] = dict(env)
    ops: List[AliasOp] = []

    for original, alias in alias_map.items():
        if original not in env:
            ops.append(AliasOp(original, alias, "", skipped=True, reason="key not found"))
            continue

        value = env[original]

        if alias in result_env and not overwrite:
            ops.append(AliasOp(original, alias, value, skipped=True, reason="alias already exists"))
            continue

        result_env[alias] = value
        if not keep_original and original in result_env and original != alias:
            del result_env[original]

        ops.append(AliasOp(original, alias, value))

    return AliasResult(ops=ops, env=result_env)
