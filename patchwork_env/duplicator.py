"""Detect and report duplicate keys within a single .env file."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DuplicateEntry:
    key: str
    occurrences: int
    values: List[str]

    def __repr__(self) -> str:
        return f"DuplicateEntry({self.key!r}, x{self.occurrences})"


@dataclass
class DuplicateResult:
    entries: List[DuplicateEntry] = field(default_factory=list)
    total_keys_scanned: int = 0

    @property
    def has_duplicates(self) -> bool:
        return len(self.entries) > 0

    @property
    def duplicate_count(self) -> int:
        return len(self.entries)


def find_duplicates(lines: List[str]) -> DuplicateResult:
    """Scan raw lines from an .env file and find duplicate key definitions."""
    seen: Dict[str, List[str]] = {}
    total = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        total += 1
        seen.setdefault(key, []).append(value)

    entries = [
        DuplicateEntry(key=k, occurrences=len(v), values=v)
        for k, v in seen.items()
        if len(v) > 1
    ]
    return DuplicateResult(entries=entries, total_keys_scanned=total)
