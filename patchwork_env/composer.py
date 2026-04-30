"""composer.py – merge multiple .env dicts into one with source tracking.

Unlike cascader (which tracks layer overrides) or merger (which detects
conflicts), the composer is a lightweight "assemble-and-annotate" step:
it joins N named envs into a single flat dict and records which source
each key came from.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ComposeEntry:
    key: str
    value: str
    source: str  # label of the env that contributed this key

    def __repr__(self) -> str:  # pragma: no cover
        return f"ComposeEntry({self.key!r}, source={self.source!r})"


@dataclass
class ComposeResult:
    entries: List[ComposeEntry] = field(default_factory=list)
    source_labels: List[str] = field(default_factory=list)

    # --- convenience accessors -------------------------------------------

    @property
    def env(self) -> Dict[str, str]:
        """Flat key→value dict of the composed result."""
        return {e.key: e.value for e in self.entries}

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    def source_for(self, key: str) -> Optional[str]:
        for e in self.entries:
            if e.key == key:
                return e.source
        return None

    def keys_from(self, label: str) -> List[str]:
        return [e.key for e in self.entries if e.source == label]


def compose_envs(
    sources: List[Tuple[str, Dict[str, str]]],
    *,
    strategy: str = "last",
) -> ComposeResult:
    """Compose *sources* into a single env.

    Parameters
    ----------
    sources:
        Ordered list of ``(label, env_dict)`` pairs.
    strategy:
        ``"last"`` – later sources win (default).
        ``"first"`` – earlier sources win.
    """
    if strategy not in ("last", "first"):
        raise ValueError(f"Unknown strategy {strategy!r}; expected 'first' or 'last'")

    merged: Dict[str, ComposeEntry] = {}

    for label, env in sources:
        for key, value in env.items():
            if strategy == "first" and key in merged:
                continue
            merged[key] = ComposeEntry(key=key, value=value, source=label)

    labels = [lbl for lbl, _ in sources]
    return ComposeResult(
        entries=list(merged.values()),
        source_labels=labels,
    )
