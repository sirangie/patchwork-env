"""caster.py — cast env values to typed Python objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


@dataclass
class CastOp:
    key: str
    raw: str
    cast_type: str
    value: Any
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        status = "ok" if self.ok else f"err:{self.error}"
        return f"CastOp({self.key!r} -> {self.cast_type} [{status}])"


@dataclass
class CastResult:
    ops: List[CastOp] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for o in self.ops if o.ok)

    @property
    def failure_count(self) -> int:
        return sum(1 for o in self.ops if not o.ok)

    @property
    def typed(self) -> Dict[str, Any]:
        """Return dict of successfully cast key -> typed value."""
        return {o.key: o.value for o in self.ops if o.ok}

    @property
    def failures(self) -> List[CastOp]:
        return [o for o in self.ops if not o.ok]


def _cast_bool(raw: str) -> bool:
    low = raw.strip().lower()
    if low in _TRUTHY:
        return True
    if low in _FALSY:
        return False
    raise ValueError(f"cannot cast {raw!r} to bool")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
) -> CastResult:
    """Cast env values according to *schema* mapping key -> type name.

    Supported types: ``str``, ``int``, ``float``, ``bool``.
    Keys not present in *schema* are returned as-is (str, ok=True).
    """
    result = CastResult()
    for key, raw in env.items():
        cast_type = schema.get(key, "str")
        try:
            if cast_type == "str":
                value: Any = raw
            elif cast_type == "int":
                value = int(raw)
            elif cast_type == "float":
                value = float(raw)
            elif cast_type == "bool":
                value = _cast_bool(raw)
            else:
                raise ValueError(f"unknown type {cast_type!r}")
            result.ops.append(CastOp(key=key, raw=raw, cast_type=cast_type, value=value, ok=True))
        except (ValueError, TypeError) as exc:
            result.ops.append(
                CastOp(key=key, raw=raw, cast_type=cast_type, value=None, ok=False, error=str(exc))
            )
    return result
