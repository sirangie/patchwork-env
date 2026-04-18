"""Audit log: record diff/sync operations to a JSONL file."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from patchwork_env.differ import DiffEntry

DEFAULT_AUDIT_FILE = ".patchwork_audit.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_diff(
    entries: List[DiffEntry],
    source: str,
    target: str,
    audit_file: Optional[str] = None,
) -> None:
    """Append a diff event to the audit log."""
    path = Path(audit_file or DEFAULT_AUDIT_FILE)
    event = {
        "event": "diff",
        "timestamp": _now_iso(),
        "source": source,
        "target": target,
        "changes": [
            {"key": e.key, "status": e.status}
            for e in entries
            if e.status != "unchanged"
        ],
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def record_sync(
    applied: List[str],
    skipped: List[str],
    target: str,
    audit_file: Optional[str] = None,
) -> None:
    """Append a sync event to the audit log."""
    path = Path(audit_file or DEFAULT_AUDIT_FILE)
    event = {
        "event": "sync",
        "timestamp": _now_iso(),
        "target": target,
        "applied": applied,
        "skipped": skipped,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def read_audit_log(audit_file: Optional[str] = None) -> List[dict]:
    """Return all events from the audit log as a list of dicts."""
    path = Path(audit_file or DEFAULT_AUDIT_FILE)
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events
