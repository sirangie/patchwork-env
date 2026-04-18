"""Rendering helpers for template output."""

from __future__ import annotations

import json
from typing import List

from .templater import TemplateEntry


def render_template_text(entries: List[TemplateEntry]) -> str:
    """Human-readable summary of what was kept vs masked."""
    lines = ["Template generation summary:", ""]
    kept = [e for e in entries if e.kept]
    masked = [e for e in entries if not e.kept]
    if kept:
        lines.append(f"  Kept ({len(kept)}):")
        for e in kept:
            lines.append(f"    {e.key}={e.placeholder}")
    if masked:
        lines.append(f"  Masked ({len(masked)}):")
        for e in masked:
            lines.append(f"    {e.key}=")
    lines.append("")
    lines.append(f"Total: {len(entries)} keys | kept: {len(kept)} | masked: {len(masked)}")
    return "\n".join(lines)


def render_template_json(entries: List[TemplateEntry]) -> str:
    """JSON representation of template entries."""
    data = [
        {
            "key": e.key,
            "placeholder": e.placeholder,
            "kept": e.kept,
        }
        for e in entries
    ]
    return json.dumps({"entries": data, "total": len(data)}, indent=2)
