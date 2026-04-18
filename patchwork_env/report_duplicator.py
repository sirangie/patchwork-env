"""Render duplicate detection results as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.duplicator import DuplicateResult


def render_duplicate_text(result: DuplicateResult) -> str:
    lines = ["=== Duplicate Key Report ==="]
    lines.append(f"Keys scanned : {result.total_keys_scanned}")
    lines.append(f"Duplicates   : {result.duplicate_count}")
    lines.append("")

    if not result.has_duplicates:
        lines.append("No duplicate keys found.")
        return "\n".join(lines)

    for entry in sorted(result.entries, key=lambda e: e.key):
        lines.append(f"  [DUP] {entry.key}  ({entry.occurrences}x)")
        for i, v in enumerate(entry.values, 1):
            lines.append(f"        #{i}: {v!r}")

    return "\n".join(lines)


def render_duplicate_json(result: DuplicateResult) -> str:
    payload = {
        "total_keys_scanned": result.total_keys_scanned,
        "duplicate_count": result.duplicate_count,
        "duplicates": [
            {"key": e.key, "occurrences": e.occurrences, "values": e.values}
            for e in result.entries
        ],
    }
    return json.dumps(payload, indent=2)
