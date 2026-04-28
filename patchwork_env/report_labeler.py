"""report_labeler.py — text and JSON renderers for LabelResult."""
from __future__ import annotations

import json
from typing import Any, Dict

from .labeler import LabelResult


def render_label_text(result: LabelResult, *, show_values: bool = False) -> str:
    lines: list[str] = []
    lines.append("=== Label Report ===")
    lines.append(
        f"Keys labeled : {result.labeled_count}"
    )
    lines.append(
        f"Total labels : {result.total_labels_applied}"
    )
    lines.append("")

    if not result.ops:
        lines.append("  (no labels applied)")
        return "\n".join(lines)

    # Group by key for display
    seen: dict[str, list[str]] = {}
    for op in result.ops:
        seen.setdefault(op.key, [])
        if op.label not in seen[op.key]:
            seen[op.key].append(op.label)

    for key, lbls in sorted(seen.items()):
        tag_str = ", ".join(lbls)
        lines.append(f"  {key}  [{tag_str}]")

    return "\n".join(lines)


def render_label_json(result: LabelResult) -> str:
    payload: Dict[str, Any] = {
        "labeled_count": result.labeled_count,
        "total_labels_applied": result.total_labels_applied,
        "labels": {
            key: sorted(lbls)
            for key, lbls in sorted(result.labels.items())
        },
        "ops": [
            {"key": op.key, "label": op.label, "matched_rule": op.matched_rule}
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
