"""defaulter.py – fill in missing keys from a defaults map."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DefaultOp:
    key: str
    value: str
    applied: bool          # True = key was missing and was filled in
    reason: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        symbol = "+" if self.applied else "="
        return f"DefaultOp({symbol} {self.key}={self.value!r})"


@dataclass
class DefaultResult:
    ops: List[DefaultOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def applied_count(self) -> int:
        return sum(1 for op in self.ops if op.applied)

    @property
    def skipped_count(self) -> int:
        return sum(1 for op in self.ops if not op.applied)

    @property
    def applied_keys(self) -> List[str]:
        return [op.key for op in self.ops if op.applied]


def apply_defaults(
    env: Dict[str, str],
    defaults: Dict[str, str],
    *,
    overwrite_empty: bool = False,
) -> DefaultResult:
    """Return a new env dict with *defaults* filled in for missing keys.

    Args:
        env: The base environment mapping.
        defaults: Key/value pairs to inject when the key is absent (or empty
                  if *overwrite_empty* is True).
        overwrite_empty: When True, also fill in defaults for keys that exist
                         but have an empty string value.
    """
    result_env: Dict[str, str] = dict(env)
    ops: List[DefaultOp] = []

    for key, default_value in defaults.items():
        existing: Optional[str] = env.get(key)
        missing = key not in env
        empty_override = overwrite_empty and existing == ""

        if missing or empty_override:
            result_env[key] = default_value
            reason = "missing" if missing else "empty"
            ops.append(DefaultOp(key=key, value=default_value, applied=True, reason=reason))
        else:
            ops.append(DefaultOp(key=key, value=existing, applied=False, reason="present"))

    return DefaultResult(ops=ops, env=result_env)
