"""Cascade multiple .env layers into a single resolved env dict.

Layers are applied left-to-right; later layers override earlier ones.
Each key tracks which layer last set it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CascadeEntry:
    key: str
    value: str
    source: str  # label of the layer that won
    overridden_by: List[str] = field(default_factory=list)  # labels that touched this key

    def __repr__(self) -> str:
        return f"CascadeEntry({self.key!r}, source={self.source!r})"


@dataclass
class CascadeResult:
    entries: List[CascadeEntry]
    layer_labels: List[str]

    @property
    def env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if len(e.overridden_by) > 1]

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    def source_for(self, key: str) -> Optional[str]:
        for e in self.entries:
            if e.key == key:
                return e.source
        return None


def cascade_envs(
    layers: List[Tuple[str, Dict[str, str]]],
) -> CascadeResult:
    """Merge layers in order. Each tuple is (label, env_dict)."""
    merged: Dict[str, CascadeEntry] = {}
    labels = [label for label, _ in layers]

    for label, env in layers:
        for key, value in env.items():
            if key in merged:
                merged[key].value = value
                merged[key].source = label
                merged[key].overridden_by.append(label)
            else:
                merged[key] = CascadeEntry(
                    key=key,
                    value=value,
                    source=label,
                    overridden_by=[label],
                )

    entries = sorted(merged.values(), key=lambda e: e.key)
    return CascadeResult(entries=entries, layer_labels=labels)
