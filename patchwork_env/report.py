"""Render diff results and validation results as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.differ import DiffEntry
from patchwork_env.validator import ValidationResult


# ── diff renderers ────────────────────────────────────────────────────────────

def render_text(entries: list[DiffEntry], *, mask: bool = False) -> str:
    lines = []
    for e in entries:
        if e.status == "unchanged":
            continue
        old = e.masked_old if mask else e.old_value
        new = e.masked_new if mask else e.new_value
        if e.status == "added":
            lines.append(f"+ {e.key}={new}")
        elif e.status == "removed":
            lines.append(f"- {e.key}={old}")
        elif e.status == "changed":
            lines.append(f"~ {e.key}: {old!r} -> {new!r}")
    return "\n".join(lines)


def render_summary(entries: list[DiffEntry]) -> str:
    from patchwork_env.differ import summary
    s = summary(entries)
    parts = [f"{v} {k}" for k, v in s.items() if v]
    return ", ".join(parts) if parts else "no differences"


def render_json(entries: list[DiffEntry], *, mask: bool = False) -> str:
    out = []
    for e in entries:
        out.append({
            "key": e.key,
            "status": e.status,
            "old": e.masked_old if mask else e.old_value,
            "new": e.masked_new if mask else e.new_value,
        })
    return json.dumps(out, indent=2)


# ── validation renderers ──────────────────────────────────────────────────────

def render_validation_text(result: ValidationResult) -> str:
    if not result.issues:
        return "validation passed — no issues found"
    lines = []
    for issue in result.issues:
        lines.append(repr(issue))
    status = "FAILED" if not result.ok else "PASSED (with warnings)"
    lines.insert(0, f"Validation {status}:")
    return "\n".join(lines)


def render_validation_json(result: ValidationResult) -> str:
    return json.dumps({
        "ok": result.ok,
        "errors": [{"key": i.key, "message": i.message} for i in result.errors],
        "warnings": [{"key": i.key, "message": i.message} for i in result.warnings],
    }, indent=2)
