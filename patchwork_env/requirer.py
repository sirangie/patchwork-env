"""requirer.py — Check which keys in an env are required vs optional vs extra."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class RequireOp:
    key: str
    status: str          # 'present', 'missing', 'extra'
    required: bool
    value: Optional[str] = None

    def __repr__(self) -> str:
        tag = "required" if self.required else "optional"
        return f"RequireOp({self.key!r}, {self.status}, {tag})"


@dataclass
class RequireResult:
    ops: List[RequireOp] = field(default_factory=list)
    allow_extras: bool = True

    @property
    def ok(self) -> bool:
        return len(self.missing_required) == 0 and (
            self.allow_extras or len(self.extra_keys) == 0
        )

    @property
    def missing_required(self) -> List[RequireOp]:
        return [o for o in self.ops if o.status == "missing" and o.required]

    @property
    def missing_optional(self) -> List[RequireOp]:
        return [o for o in self.ops if o.status == "missing" and not o.required]

    @property
    def present_keys(self) -> List[RequireOp]:
        return [o for o in self.ops if o.status == "present"]

    @property
    def extra_keys(self) -> List[RequireOp]:
        return [o for o in self.ops if o.status == "extra"]


def require_env(
    env: Dict[str, str],
    required: List[str],
    optional: Optional[List[str]] = None,
    allow_extras: bool = True,
) -> RequireResult:
    """Validate env against a list of required and optional keys."""
    optional_set: Set[str] = set(optional or [])
    required_set: Set[str] = set(required)
    known: Set[str] = required_set | optional_set

    ops: List[RequireOp] = []

    for key in required:
        if key in env:
            ops.append(RequireOp(key=key, status="present", required=True, value=env[key]))
        else:
            ops.append(RequireOp(key=key, status="missing", required=True))

    for key in (optional or []):
        if key in env:
            ops.append(RequireOp(key=key, status="present", required=False, value=env[key]))
        else:
            ops.append(RequireOp(key=key, status="missing", required=False))

    for key, val in env.items():
        if key not in known:
            ops.append(RequireOp(key=key, status="extra", required=False, value=val))

    return RequireResult(ops=ops, allow_extras=allow_extras)
