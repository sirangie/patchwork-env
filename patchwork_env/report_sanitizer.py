"""report_sanitizer.py — text and JSON rendering for SanitizeResult."""
from __future__ import annotations

import json
from typing import Any, Dict

from patchwork_env.sanitizer import SanitizeResult


def render_sanitize_text(result: SanitizeResult, *, show_values: bool = False) -> str:
    lines: list[str] = []
    lines.append("=== Sanitize Report ===")
    lines.append(
        f"Total keys: {len(result.ops)}  "
        f"changed: {result.changed_count}  "
        f"unchanged: {result.unchanged_count}"
    )
    lines.append("")

    for op in result.ops:
        if op.changed:
            marker = "~"
            detail = ", ".join(op.reasons)
            if show_values:
                lines.append(f"  {marker} {op.key}: {op.original!r} -> {op.sanitized!r}  [{detail}]")
            else:
                lines.append(f"  {marker} {op.key}  [{detail}]")
        else:
            lines.append(f"  = {op.key}")

    return "\n".join(lines)


def render_sanitize_json(result: SanitizeResult) -> str:
    payload: Dict[str, Any] = {
        "summary": {
            "total": len(result.ops),
            "changed": result.changed_count,
            "unchanged": result.unchanged_count,
        },
        "ops": [
            {
                "key": op.key,
                "changed": op.changed,
                "reasons": op.reasons,
                "original": op.original if op.changed else None,
                "sanitized": op.sanitized if op.changed else None,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
