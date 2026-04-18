"""Compare two env snapshots or files and produce a structured comparison report."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CompareEntry:
    key: str
    left: Optional[str]
    right: Optional[str]

    @property
    def status(self) -> str:
        if self.left is None:
            return "added"
        if self.right is None:
            return "removed"
        if self.left == self.right:
            return "same"
        return "changed"

    def __repr__(self) -> str:
        return f"CompareEntry({self.key!r}, status={self.status!r})"


@dataclass
class CompareResult:
    entries: List[CompareEntry] = field(default_factory=list)
    left_label: str = "left"
    right_label: str = "right"

    @property
    def added(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def same(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "same"]

    @property
    def is_identical(self) -> bool:
        return len(self.added) == 0 and len(self.removed) == 0 and len(self.changed) == 0


def compare_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> CompareResult:
    all_keys = sorted(set(left) | set(right))
    entries = [
        CompareEntry(key=k, left=left.get(k), right=right.get(k))
        for k in all_keys
    ]
    return CompareResult(entries=entries, left_label=left_label, right_label=right_label)
