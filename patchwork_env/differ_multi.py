"""Multi-env diff: compare a base env against multiple target envs."""
from dataclasses import dataclass, field
from typing import Dict, List
from .differ import DiffEntry, diff_envs


@dataclass
class MultiDiffResult:
    base_label: str
    results: Dict[str, List[DiffEntry]] = field(default_factory=dict)

    def labels(self) -> List[str]:
        return list(self.results.keys())

    def for_env(self, label: str) -> List[DiffEntry]:
        return self.results.get(label, [])

    def all_keys(self) -> List[str]:
        keys = set()
        for entries in self.results.values():
            for e in entries:
                keys.add(e.key)
        return sorted(keys)

    def changed_in(self, label: str) -> List[DiffEntry]:
        return [e for e in self.for_env(label) if e.status != "unchanged"]

    def summary(self) -> Dict[str, Dict[str, int]]:
        out = {}
        for label, entries in self.results.items():
            counts: Dict[str, int] = {}
            for e in entries:
                counts[e.status] = counts.get(e.status, 0) + 1
            out[label] = counts
        return out


def diff_multi(
    base: Dict[str, str],
    targets: Dict[str, Dict[str, str]],
    mask: bool = False,
    base_label: str = "base",
) -> MultiDiffResult:
    """Diff base env against each target env in the targets dict."""
    result = MultiDiffResult(base_label=base_label)
    for label, target in targets.items():
        result.results[label] = diff_envs(base, target, mask=mask)
    return result
