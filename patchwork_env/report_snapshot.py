"""Render snapshot comparison reports."""
from __future__ import annotations

import json
from typing import List


def render_snapshot_text(old: dict, new: dict, changes: List[dict]) -> str:
    lines = []
    lines.append(f"Snapshot comparison")
    lines.append(f"  From : {old.get('label') or old.get('timestamp', '?')}")
    lines.append(f"  To   : {new.get('label') or new.get('timestamp', '?')}")
    lines.append("")
    if not changes:
        lines.append("  No changes detected.")
        return "\n".join(lines)
    for c in changes:
        status = c["status"].upper()
        key = c["key"]
        if c["status"] == "added":
            lines.append(f"  + {key}  (added)")
        elif c["status"] == "removed":
            lines.append(f"  - {key}  (removed)")
        else:
            lines.append(f"  ~ {key}  (changed)")
    lines.append("")
    lines.append(f"  {len(changes)} change(s) total.")
    return "\n".join(lines)


def render_snapshot_json(old: dict, new: dict, changes: List[dict]) -> str:
    payload = {
        "from": old.get("label") or old.get("timestamp"),
        "to": new.get("label") or new.get("timestamp"),
        "change_count": len(changes),
        "changes": changes,
    }
    return json.dumps(payload, indent=2)
