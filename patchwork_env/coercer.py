"""coercer.py — coerce env values to typed Python objects.

Supports bool, int, float, list (comma-separated), and str (default).
Each CoerceOp records the original string, the target type, the coerced
value (or None on failure), and whether the coercion succeeded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Recognised truthy / falsy strings for bool coercion
_TRUTHY = {"1", "true", "yes", "on"}
_FALSY  = {"0", "false", "no", "off"}


@dataclass
class CoerceOp:
    key: str
    original: str
    target_type: str          # "bool" | "int" | "float" | "list" | "str"
    coerced: Optional[Any]    # None when coercion failed
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        status = "ok" if self.ok else f"err:{self.error}"
        return f"<CoerceOp {self.key} {self.original!r} -> {self.target_type} [{status}]>"


@dataclass
class CoerceResult:
    ops: List[CoerceOp] = field(default_factory=list)
    # env is the final dict with coerced values where successful, originals
    # elsewhere — callers decide what to do with failures.
    env: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_count(self) -> int:
        return sum(1 for op in self.ops if op.ok)

    @property
    def failure_count(self) -> int:
        return sum(1 for op in self.ops if not op.ok)

    @property
    def failed_keys(self) -> List[str]:
        return [op.key for op in self.ops if not op.ok]


def _coerce_bool(value: str) -> tuple[bool, Optional[str]]:
    """Return (coerced_bool, error_or_None)."""
    lower = value.strip().lower()
    if lower in _TRUTHY:
        return True, None
    if lower in _FALSY:
        return False, None
    return False, f"cannot coerce {value!r} to bool"


def _coerce_one(key: str, value: str, target_type: str) -> CoerceOp:
    """Attempt to coerce *value* to *target_type* and return a CoerceOp."""
    try:
        if target_type == "bool":
            coerced, err = _coerce_bool(value)
            if err:
                return CoerceOp(key, value, target_type, None, False, err)
            return CoerceOp(key, value, target_type, coerced, True)

        if target_type == "int":
            return CoerceOp(key, value, target_type, int(value), True)

        if target_type == "float":
            return CoerceOp(key, value, target_type, float(value), True)

        if target_type == "list":
            items = [item.strip() for item in value.split(",")]
            return CoerceOp(key, value, target_type, items, True)

        # default: str — always succeeds
        return CoerceOp(key, value, target_type, value, True)

    except (ValueError, TypeError) as exc:
        return CoerceOp(key, value, target_type, None, False, str(exc))


def coerce_env(
    env: Dict[str, str],
    type_map: Dict[str, str],
    *,
    fallback_to_original: bool = True,
) -> CoerceResult:
    """Coerce values in *env* according to *type_map*.

    Parameters
    ----------
    env:
        Source env dict (str -> str).
    type_map:
        Mapping of key -> target type string.  Keys absent from *type_map*
        are passed through as ``str`` without recording an op.
    fallback_to_original:
        When True (default) a failed coercion leaves the original string in
        ``result.env``; when False the key is omitted from ``result.env``.
    """
    result = CoerceResult()

    # Start with a shallow copy; we'll overwrite coerced keys below.
    result.env = dict(env)

    for key, target_type in type_map.items():
        if key not in env:
            # Key not present — nothing to coerce.
            continue

        op = _coerce_one(key, env[key], target_type)
        result.ops.append(op)

        if op.ok:
            result.env[key] = op.coerced
        elif not fallback_to_original:
            result.env.pop(key, None)
        # else: original string stays in result.env

    return result
