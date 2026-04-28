"""labeler.py — attach arbitrary labels/tags to env keys based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class LabelOp:
    key: str
    label: str
    matched_rule: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"LabelOp({self.key!r} -> {self.label!r} via {self.matched_rule!r})"


@dataclass
class LabelResult:
    ops: List[LabelOp] = field(default_factory=list)
    labels: Dict[str, List[str]] = field(default_factory=dict)  # key -> [label, ...]

    @property
    def labeled_count(self) -> int:
        return len({op.key for op in self.ops})

    @property
    def total_labels_applied(self) -> int:
        return len(self.ops)

    def labels_for(self, key: str) -> List[str]:
        return self.labels.get(key, [])


def label_env(
    env: Dict[str, str],
    rules: Dict[str, str],  # pattern -> label
    *,
    case_sensitive: bool = False,
) -> LabelResult:
    """Apply label rules to env keys.

    Args:
        env: The parsed env dict.
        rules: Mapping of regex pattern -> label string.
        case_sensitive: Whether pattern matching is case-sensitive.

    Returns:
        LabelResult with ops and per-key label lists.
    """
    result = LabelResult()
    flags = 0 if case_sensitive else re.IGNORECASE

    for key in env:
        for pattern, label in rules.items():
            if re.search(pattern, key, flags):
                op = LabelOp(key=key, label=label, matched_rule=pattern)
                result.ops.append(op)
                result.labels.setdefault(key, [])
                if label not in result.labels[key]:
                    result.labels[key].append(label)

    return result
