"""Promote keys from one environment tier to another with optional guards."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PromoteOp:
    key: str
    value: str
    source_value: Optional[str]
    action: str  # 'promoted', 'skipped', 'blocked'
    reason: str = ""

    def __repr__(self) -> str:
        return f"PromoteOp({self.action} {self.key!r}: {self.reason or 'ok'})"


@dataclass
class PromoteResult:
    ops: List[PromoteOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def promoted_count(self) -> int:
        return sum(1 for o in self.ops if o.action == "promoted")

    @property
    def skipped_count(self) -> int:
        return sum(1 for o in self.ops if o.action == "skipped")

    @property
    def blocked_count(self) -> int:
        return sum(1 for o in self.ops if o.action == "blocked")

    @property
    def promoted_keys(self) -> List[str]:
        return [o.key for o in self.ops if o.action == "promoted"]


def promote_env(
    source: Dict[str, str],
    target: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
    guard_empty: bool = True,
    blocked_keys: Optional[List[str]] = None,
) -> PromoteResult:
    """Promote keys from *source* into *target*.

    Args:
        source: The environment to promote values from.
        target: The destination environment (not mutated; result in .env).
        keys: If given, only these keys are considered.
        overwrite: Allow overwriting keys already present in target.
        guard_empty: Skip keys whose source value is empty.
        blocked_keys: Keys that must never be promoted.
    """
    blocked = set(blocked_keys or [])
    candidates = keys if keys is not None else list(source.keys())
    result_env = dict(target)
    ops: List[PromoteOp] = []

    for key in candidates:
        src_val = source.get(key)
        if src_val is None:
            ops.append(PromoteOp(key, "", None, "skipped", "not in source"))
            continue
        if key in blocked:
            ops.append(PromoteOp(key, src_val, target.get(key), "blocked", "key is blocked"))
            continue
        if guard_empty and src_val == "":
            ops.append(PromoteOp(key, src_val, target.get(key), "skipped", "empty value"))
            continue
        if key in target and not overwrite:
            ops.append(PromoteOp(key, src_val, target[key], "skipped", "already exists"))
            continue
        result_env[key] = src_val
        ops.append(PromoteOp(key, src_val, target.get(key), "promoted"))

    return PromoteResult(ops=ops, env=result_env)
