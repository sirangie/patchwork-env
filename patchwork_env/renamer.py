"""Rename keys across an env dict, with optional value transform."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameOp:
    old_key: str
    new_key: str
    value: str
    status: str  # 'renamed' | 'skipped' | 'conflict'

    def __repr__(self) -> str:
        return f"RenameOp({self.old_key!r} -> {self.new_key!r}, {self.status})"


@dataclass
class RenameResult:
    env: Dict[str, str]
    ops: List[RenameOp] = field(default_factory=list)

    @property
    def renamed(self) -> List[RenameOp]:
        return [o for o in self.ops if o.status == "renamed"]

    @property
    def skipped(self) -> List[RenameOp]:
        return [o for o in self.ops if o.status == "skipped"]

    @property
    def conflicts(self) -> List[RenameOp]:
        return [o for o in self.ops if o.status == "conflict"]


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> RenameResult:
    """Rename keys in *env* according to *mapping* {old: new}.

    If the new key already exists and *overwrite* is False the op is
    recorded as a conflict and the env is left unchanged for that key.
    """
    result = dict(env)
    ops: List[RenameOp] = []

    for old_key, new_key in mapping.items():
        if old_key not in result:
            ops.append(RenameOp(old_key, new_key, "", "skipped"))
            continue

        value = result[old_key]

        if new_key in result and not overwrite:
            ops.append(RenameOp(old_key, new_key, value, "conflict"))
            continue

        del result[old_key]
        result[new_key] = value
        ops.append(RenameOp(old_key, new_key, value, "renamed"))

    return RenameResult(env=result, ops=ops)
