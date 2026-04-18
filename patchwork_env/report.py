"""Render diff, validation, audit, and merge results as text or JSON."""
from __future__ import annotations
import json
from typing, Dict, List

from patchwork_env.differ import DiffEntry
from patchwork_env.validator import ValidationResult
from patchwork_env.merger import MergeResult


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------

def render_text(entries: List[DiffEntry], mask: bool = False) -> str:
    lines = []
    for e in entries:
        lines.append(str(e) if not mask else repr(e))
    return "\n".join(lines)


def render_summary(entries: List[DiffEntry]) -> str:
    from patchwork_env.differ import summary
    s = summary(entries)
    parts = [f"{v} {k}" for k, v in s.items()]
    return "  ".join(parts)


def render_json(entries: List[DiffEntry], mask: bool = False) -> str:
    data = [
        {
            "key": e.key,
            "status": e.status,
            "source": e.source_value if not mask else "***",
            "target": e.target_value if not mask else "***",
        }
        for e in entries
    ]
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def render_validation_text(result: ValidationResult) -> str:
    if result.ok:
        return "✓ No issues found."
    lines = []
    for issue in result.issues:
        tag = "ERROR" if issue.level == "error" else "WARN "
        lines.append(f"[{tag}] {issue.key}: {issue.message}")
    return "\n".join(lines)


def render_validation_json(result: ValidationResult) -> str:
    data: Dict[str, Any] = {
        "ok": result.ok,
        "issues": [
            {"level": i.level, "key": i.key, "message": i.message}
            for i in result.issues
        ],
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def render_audit_text(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "No audit events recorded."
    lines = []
    for ev in events:
        lines.append(f"[{ev['timestamp']}] {ev['event'].upper()}  {ev.get('source', '')} -> {ev.get('target', '')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def render_merge_text(result: MergeResult) -> str:
    lines = [f"Merged {len(result.merged)} keys."]
    if result.has_conflicts:
        lines.append(f"Conflicts ({len(result.conflicts)}):")
        for key, entries in result.conflicts:
            lines.append(f"  {key}:")
            for name, val in entries:
                lines.append(f"    [{name}] {val}")
    else:
        lines.append("No conflicts.")
    return "\n".join(lines)


def render_merge_json(result: MergeResult) -> str:
    data = {
        "merged": result.merged,
        "sources": result.sources,
        "conflicts": [
            {"key": k, "values": [{"file": n, "value": v} for n, v in entries]}
            for k, entries in result.conflicts
        ],
    }
    return json.dumps(data, indent=2)
