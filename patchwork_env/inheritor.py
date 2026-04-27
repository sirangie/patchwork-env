"""inheritor.py — inherit keys from a parent env into a child env."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InheritOp:
    key: str
    value: str
    source: str  # 'parent' | 'child' | 'override'
    overwritten: bool = False

    def __repr__(self) -> str:
        tag = "overwrite" if self.overwritten else self.source
        return f"<InheritOp {self.key}={self.value!r} [{tag}]>"


@dataclass
class InheritResult:
    ops: List[InheritOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def inherited_count(self) -> int:
        return sum(1 for op in self.ops if op.source == "parent" and not op.overwritten)

    @property
    def overwritten_count(self) -> int:
        return sum(1 for op in self.ops if op.overwritten)

    @property
    def child_only_count(self) -> int:
        return sum(1 for op in self.ops if op.source == "child")

    def inherited_keys(self) -> List[str]:
        return [op.key for op in self.ops if op.source == "parent" and not op.overwritten]

    def overwritten_keys(self) -> List[str]:
        return [op.key for op in self.ops if op.overwritten]


def inherit_env(
    parent: Dict[str, str],
    child: Dict[str, str],
    overwrite: bool = False,
    skip_empty_parent: bool = True,
) -> InheritResult:
    """Merge parent keys into child. Child values win unless overwrite=True."""
    result = InheritResult()
    merged: Dict[str, str] = {}

    all_keys = list(child.keys()) + [k for k in parent if k not in child]

    for key in all_keys:
        in_parent = key in parent
        in_child = key in child
        parent_val = parent.get(key, "")
        child_val = child.get(key, "")

        if skip_empty_parent and in_parent and parent_val == "" and not in_child:
            continue

        if in_child and in_parent:
            if overwrite:
                merged[key] = parent_val
                result.ops.append(InheritOp(key, parent_val, "override", overwritten=True))
            else:
                merged[key] = child_val
                result.ops.append(InheritOp(key, child_val, "child"))
        elif in_child:
            merged[key] = child_val
            result.ops.append(InheritOp(key, child_val, "child"))
        else:
            merged[key] = parent_val
            result.ops.append(InheritOp(key, parent_val, "parent"))

    result.env = merged
    return result
