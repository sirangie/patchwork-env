"""Merge multiple .env files with priority ordering."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MergeResult:
    merged: Dict[str, str]
    sources: Dict[str, str]  # key -> which file it came from
    conflicts: List[Tuple[str, List[Tuple[str, str]]]]  # key -> [(file, value)]

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def merge_envs(
    envs: List[Tuple[str, Dict[str, str]]],
    strategy: str = "last-wins",
) -> MergeResult:
    """Merge a list of (name, env_dict) pairs.

    strategy:
      - 'last-wins'  : later files override earlier ones (default)
      - 'first-wins' : earlier files take priority
    """
    if strategy not in ("last-wins", "first-wins"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    conflict_map: Dict[str, List[Tuple[str, str]]] = {}

    ordered = envs if strategy == "last-wins" else list(reversed(envs))

    # collect all keys that appear in more than one file
    key_files: Dict[str, List[str]] = {}
    for name, env in envs:
        for k in env:
            key_files.setdefault(k, []).append(name)

    for name, env in ordered:
        for k, v in env.items():
            if k not in merged:
                merged[k] = v
                sources[k] = name

    # record conflicts (keys defined in multiple files with different values)
    for k, files in key_files.items():
        if len(files) > 1:
            values = [(name, env[k]) for name, env in envs if k in env]
            unique_vals = {v for _, v in values}
            if len(unique_vals) > 1:
                conflict_map[k] = values

    conflicts = list(conflict_map.items())
    return MergeResult(merged=merged, sources=sources, conflicts=conflicts)
