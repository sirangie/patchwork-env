"""Render SchemaDiffResult as text or JSON."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.differ_schema import SchemaDiffResult

_STATUS_SYMBOL = {
    "ok": "✓",
    "missing_required": "✗",
    "missing_optional": "?",
    "extra": "+",
}


def render_schema_diff_text(
    result: SchemaDiffResult,
    show_descriptions: bool = True,
) -> str:
    lines = [
        f"Schema Diff  [{result.env_label}] vs [{result.schema_label}]",
        "-" * 52,
    ]

    for e in sorted(result.entries, key=lambda x: x.key):
        sym = _STATUS_SYMBOL.get(e.status, " ")
        suffix = ""
        if show_descriptions and e.description:
            suffix = f"  # {e.description}"
        if e.status == "missing_required" and e.default is not None:
            suffix += f"  (default: {e.default!r})"
        lines.append(f"  {sym} {e.key}{suffix}")

    lines.append("")
    if result.ok:
        lines.append("Status: OK — all required keys present")
    else:
        n = len(result.missing_required)
        lines.append(f"Status: FAIL — {n} required key(s) missing")

    summary_parts = [
        f"ok={len(result.ok_keys)}",
        f"missing_required={len(result.missing_required)}",
        f"missing_optional={len(result.missing_optional)}",
        f"extra={len(result.extra_keys)}",
    ]
    lines.append("  " + "  ".join(summary_parts))
    return "\n".join(lines)


def render_schema_diff_json(result: SchemaDiffResult) -> str:
    data: Dict[str, Any] = {
        "env_label": result.env_label,
        "schema_label": result.schema_label,
        "ok": result.ok,
        "summary": {
            "ok": len(result.ok_keys),
            "missing_required": len(result.missing_required),
            "missing_optional": len(result.missing_optional),
            "extra": len(result.extra_keys),
        },
        "entries": [
            {
                "key": e.key,
                "status": e.status,
                "description": e.description,
                "default": e.default,
            }
            for e in result.entries
        ],
    }
    return json.dumps(data, indent=2)
