"""Apply a patch (set of key overrides) to an env dict, with dry-run support."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchOp:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    action: str  # 'set' | 'delete' | 'skip'

    def __repr__(self) -> str:
        return f"PatchOp({self.action} {self.key!r}: {self.old_value!r} -> {self.new_value!r})"


@dataclass
class PatchResult:
    env: Dict[str, str]
    ops: List[PatchOp] = field(default_factory=list)

    @property
    def applied(self) -> List[PatchOp]:
        return [o for o in self.ops if o.action != 'skip']

    @property
    def skipped(self) -> List[PatchOp]:
        return [o for o in self.ops if o.action == 'skip']


def apply_patch(
    base: Dict[str, str],
    patch: Dict[str, Optional[str]],
    *,
    overwrite: bool = True,
    delete_none: bool = True,
) -> PatchResult:
    """Apply patch onto base env.

    patch values of None mean delete the key (when delete_none=True).
    If overwrite=False, existing keys are skipped.
    """
    result = dict(base)
    ops: List[PatchOp] = []

    for key, value in patch.items():
        old = result.get(key)

        if value is None and delete_none:
            if key in result:
                del result[key]
                ops.append(PatchOp(key, old, None, 'delete'))
            else:
                ops.append(PatchOp(key, None, None, 'skip'))
        elif key in result and not overwrite:
            ops.append(PatchOp(key, old, value, 'skip'))
        else:
            result[key] = value  # type: ignore[assignment]
            ops.append(PatchOp(key, old, value, 'set'))

    return PatchResult(env=result, ops=ops)


def patch_summary(result: PatchResult) -> str:
    sets = sum(1 for o in result.ops if o.action == 'set')
    deletes = sum(1 for o in result.ops if o.action == 'delete')
    skips = sum(1 for o in result.ops if o.action == 'skip')
    return f"{sets} set, {deletes} deleted, {skips} skipped"
