"""Render diff/sync/validation results as text or JSON."""
from __future__ import annotations

import json
from typing import List

from patchwork_env.differ import DiffEntry
from patchwork_env.validator import ValidationResult


def render_text(entries: List[DiffEntry]) -> str:
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for e in entries:
        sym = symbols.get(e.status, "?")
        if e.status == "changed":
            lines.append(f"{sym} {e.key}: {e.old_value!r} -> {e.new_value!r}")
        elif e.status == "added":
            lines.append(f"{sym} {e.key}: {e.new_value!r}")
        elif e.status == "removed":
            lines.append(f"{sym} {e.key}: {e.old_value!r}")
        else:
            lines.append(f"{sym} {e.key}")
    return "\n".join(lines)


def render_summary(entries: List[DiffEntry]) -> str:
    from patchwork_env.differ import summary
    s = summary(entries)
    parts = []
    for k, v in s.items():
        parts.append(f"{k}: {v}")
    return "  ".join(parts)


def render_json(entries: List[DiffEntry]) -> str:
    data = [
        {
            "key": e.key,
            "status": e.status,
            "old_value": e.old_value,
            "new_value": e.new_value,
        }
        for e in entries
    ]
    return json.dumps(data, indent=2)


def render_validation_text(result: ValidationResult) -> str:
    if result.ok:
        return "OK: all required keys present"
    lines = []
    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN"
        lines.append(f"[{prefix}] {issue.key}: {issue.message}")
    return "\n".join(lines)


def render_validation_json(result: ValidationResult) -> str:
    data = {
        "ok": result.ok,
        "issues": [
            {"key": i.key, "level": i.level, "message": i.message}
            for i in result.issues
        ],
    }
    return json.dumps(data, indent=2)


def render_audit_text(events: list) -> str:
    """Render audit log events as human-readable text."""
    if not events:
        return "No audit events recorded."
    lines = []
    for ev in events:
        ts = ev.get("timestamp", "?")
        kind = ev.get("event", "?")
        if kind == "diff":
            src = ev.get("source", "?")
            tgt = ev.get("target", "?")
            n = len(ev.get("changes", []))
            lines.append(f"[{ts}] diff  {src} -> {tgt}  ({n} changes)")
        elif kind == "sync":
            tgt = ev.get("target", "?")
            applied = len(ev.get("applied", []))
            skipped = len(ev.get("skipped", []))
            lines.append(f"[{ts}] sync  -> {tgt}  applied={applied} skipped={skipped}")
        else:
            lines.append(f"[{ts}] {kind}")
    return "\n".join(lines)
