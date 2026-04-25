"""substitutor.py – replace placeholder values in an env dict using a mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SubstituteOp:
    key: str
    old_value: str
    new_value: str
    placeholder: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"SubstituteOp({self.key!r}: {self.old_value!r} -> {self.new_value!r})"


@dataclass
class SubstituteResult:
    ops: List[SubstituteOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def substituted_count(self) -> int:
        return len(self.ops)

    @property
    def substituted_keys(self) -> List[str]:
        return [op.key for op in self.ops]

    @property
    def unchanged_count(self) -> int:
        return len(self.env) - self.substituted_count


def substitute_env(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    placeholder: Optional[str] = None,
    only_placeholders: bool = False,
) -> SubstituteResult:
    """Replace values in *env* using *mapping* (key -> new_value).

    If *placeholder* is given and *only_placeholders* is True, only keys whose
    current value equals the placeholder string are substituted.
    """
    result_env: Dict[str, str] = dict(env)
    ops: List[SubstituteOp] = []

    for key, new_value in mapping.items():
        if key not in result_env:
            continue
        old_value = result_env[key]
        effective_placeholder = placeholder if placeholder is not None else ""
        if only_placeholders and old_value != effective_placeholder:
            continue
        if old_value == new_value:
            continue
        result_env[key] = new_value
        ops.append(
            SubstituteOp(
                key=key,
                old_value=old_value,
                new_value=new_value,
                placeholder=effective_placeholder,
            )
        )

    return SubstituteResult(ops=ops, env=result_env)
