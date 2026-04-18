"""Snapshot: capture and compare .env state at a point in time."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def take_snapshot(env: Dict[str, str], label: str = "") -> dict:
    """Return a snapshot dict for the given env mapping."""
    return {
        "label": label,
        "timestamp": _now_iso(),
        "keys": sorted(env.keys()),
        "values": dict(env),
    }


def save_snapshot(snapshot: dict, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
        fh.write("\n")


def load_snapshot(path: str) -> dict:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def compare_snapshots(old: dict, new: dict) -> List[dict]:
    """Return a list of change records between two snapshots."""
    old_vals: Dict[str, str] = old.get("values", {})
    new_vals: Dict[str, str] = new.get("values", {})
    all_keys = sorted(set(old_vals) | set(new_vals))
    changes = []
    for key in all_keys:
        o = old_vals.get(key)
        n = new_vals.get(key)
        if o == n:
            continue
        if o is None:
            status = "added"
        elif n is None:
            status = "removed"
        else:
            status = "changed"
        changes.append({"key": key, "status": status, "old": o, "new": n})
    return changes
