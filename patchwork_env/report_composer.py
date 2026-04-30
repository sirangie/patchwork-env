"""report_composer.py – text and JSON renderers for ComposeResult."""
from __future__ import annotations

import json
from typing import Any, Dict

from .composer import ComposeResult


def render_compose_text(
    result: ComposeResult,
    *,
    show_values: bool = False,
    show_source: bool = True,
) -> str:
    lines: list[str] = []
    lines.append("=== Compose Result ===")
    lines.append(
        f"Sources : {', '.join(result.source_labels) or '(none)'}"
    )
    lines.append(f"Total keys: {result.total_keys}")
    lines.append("")

    for entry in sorted(result.entries, key=lambda e: e.key):
        parts = [entry.key]
        if show_values:
            parts.append(f"= {entry.value}")
        if show_source:
            parts.append(f"[{entry.source}]")
        lines.append("  " + "  ".join(parts))

    if not result.entries:
        lines.append("  (no keys)")

    return "\n".join(lines)


def render_compose_json(result: ComposeResult) -> str:
    data: Dict[str, Any] = {
        "source_labels": result.source_labels,
        "total_keys": result.total_keys,
        "entries": [
            {"key": e.key, "value": e.value, "source": e.source}
            for e in sorted(result.entries, key=lambda e: e.key)
        ],
    }
    return json.dumps(data, indent=2)
