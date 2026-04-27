"""archiver.py — bundle multiple env files into a single JSON archive, or restore them."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from patchwork_env.parser import parse_env_file, serialize_env


@dataclass
class ArchiveEntry:
    name: str
    env: Dict[str, str]

    def __repr__(self) -> str:  # pragma: no cover
        return f"ArchiveEntry(name={self.name!r}, keys={list(self.env)})"


@dataclass
class ArchiveResult:
    entries: List[ArchiveEntry] = field(default_factory=list)
    source_paths: List[str] = field(default_factory=list)

    @property
    def names(self) -> List[str]:
        return [e.name for e in self.entries]

    @property
    def total_keys(self) -> int:
        return sum(len(e.env) for e in self.entries)

    def get(self, name: str) -> Optional[ArchiveEntry]:
        for e in self.entries:
            if e.name == name:
                return e
        return None


def archive_files(paths: List[Path]) -> ArchiveResult:
    """Read multiple .env files and bundle them into an ArchiveResult."""
    entries: List[ArchiveEntry] = []
    source_paths: List[str] = []
    for p in paths:
        env = parse_env_file(p)
        entries.append(ArchiveEntry(name=p.name, env=env))
        source_paths.append(str(p))
    return ArchiveResult(entries=entries, source_paths=source_paths)


def save_archive(result: ArchiveResult, dest: Path) -> None:
    """Serialize an ArchiveResult to a JSON file."""
    payload = {
        "source_paths": result.source_paths,
        "entries": [
            {"name": e.name, "env": e.env}
            for e in result.entries
        ],
    }
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_archive(src: Path) -> ArchiveResult:
    """Load an ArchiveResult from a JSON archive file."""
    payload = json.loads(src.read_text(encoding="utf-8"))
    entries = [
        ArchiveEntry(name=item["name"], env=item["env"])
        for item in payload.get("entries", [])
    ]
    return ArchiveResult(entries=entries, source_paths=payload.get("source_paths", []))


def restore_archive(result: ArchiveResult, dest_dir: Path) -> List[Path]:
    """Write each archived env back to dest_dir/<name>. Returns list of written paths."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for entry in result.entries:
        out = dest_dir / entry.name
        out.write_text(serialize_env(entry.env), encoding="utf-8")
        written.append(out)
    return written
