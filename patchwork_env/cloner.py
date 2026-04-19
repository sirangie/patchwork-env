"""cloner.py – duplicate an env dict under a new key prefix."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CloneOp:
    original_key: str
    cloned_key: str
    value: str
    skipped: bool = False
    reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        tag = "SKIP" if self.skipped else "CLONE"
        return f"<CloneOp {tag} {self.original_key!r} -> {self.cloned_key!r}>"


@dataclass
class CloneResult:
    ops: List[CloneOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def cloned_count(self) -> int:
        return sum(1 for o in self.ops if not o.skipped)

    @property
    def skipped_count(self) -> int:
        return sum(1 for o in self.ops if o.skipped)

    @property
    def cloned_keys(self) -> List[str]:
        return [o.cloned_key for o in self.ops if not o.skipped]


def clone_env(
    env: Dict[str, str],
    source_prefix: str,
    target_prefix: str,
    *,
    overwrite: bool = False,
    strip_source_prefix: bool = True,
) -> CloneResult:
    """Copy keys matching *source_prefix* into *target_prefix* equivalents.

    Parameters
    ----------
    env:                The full env dict to operate on.
    source_prefix:      Only keys starting with this prefix are cloned.
    target_prefix:      Replacement prefix for the new keys.
    overwrite:          If False (default) skip keys that already exist.
    strip_source_prefix: When True the source prefix is replaced; when False
                         the target prefix is prepended to the full key name.
    """
    result = CloneResult(env=dict(env))

    for key, value in env.items():
        if not key.startswith(source_prefix):
            continue

        if strip_source_prefix:
            suffix = key[len(source_prefix):]
            new_key = f"{target_prefix}{suffix}"
        else:
            new_key = f"{target_prefix}{key}"

        if new_key in env and not overwrite:
            result.ops.append(CloneOp(key, new_key, value, skipped=True, reason="exists"))
            continue

        result.env[new_key] = value
        result.ops.append(CloneOp(key, new_key, value))

    return result
