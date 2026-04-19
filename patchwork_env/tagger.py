"""Tag keys in an env dict with arbitrary labels for grouping or filtering."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TagEntry:
    key: str
    value: str
    tags: List[str]

    def __repr__(self) -> str:  # pragma: no cover
        return f"TagEntry({self.key!r}, tags={self.tags})"


@dataclass
class TagResult:
    entries: List[TagEntry]
    tag_map: Dict[str, List[str]]  # tag -> [keys]

    def keys_for(self, tag: str) -> List[str]:
        return self.tag_map.get(tag, [])

    def tags_for(self, key: str) -> List[str]:
        for e in self.entries:
            if e.key == key:
                return e.tags
        return []

    @property
    def all_tags(self) -> List[str]:
        return sorted(self.tag_map.keys())


def tag_env(
    env: Dict[str, str],
    rules: Optional[Dict[str, List[str]]] = None,
) -> TagResult:
    """Tag each key according to rules mapping tag->list-of-key-patterns.

    A pattern matches if the key starts with the pattern (case-insensitive).
    If no rules given, an empty tag set is assigned to every key.
    """
    if rules is None:
        rules = {}

    # Build reverse index: key -> tags
    key_tags: Dict[str, List[str]] = {k: [] for k in env}
    for tag, patterns in rules.items():
        for key in env:
            for pat in patterns:
                if key.lower().startswith(pat.lower()):
                    if tag not in key_tags[key]:
                        key_tags[key].append(tag)

    entries = [
        TagEntry(key=k, value=env[k], tags=sorted(key_tags[k]))
        for k in env
    ]

    tag_map: Dict[str, List[str]] = {}
    for e in entries:
        for t in e.tags:
            tag_map.setdefault(t, []).append(e.key)

    return TagResult(entries=entries, tag_map=tag_map)
