"""Render FlattenResult as text or JSON."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.flattener import FlattenResult


def render_flatten_text(result: FlattenResult, show_values: bool = False) -> str:
    lines = ["=== Flatten Report ==="]
    lines.append(f"Total keys : {len(result.ops)}")
    lines.append(f"Renamed    : {result.changed_count}")
    lines.append(f"Unchanged  : {result.unchanged_count}")

    if result.ops:
        lines.append("")
        for op in result.ops:
            if op.changed:
                suffix = f" = {op.value!r}" if show_values else ""
                lines.append(f"  ~ {op.original_key} -> {op.flat_key}{suffix}")
            else:
                suffix = f" = {op.value!r}" if show_values else ""
                lines.append(f"  = {op.flat_key}{suffix}")

    return "\n".join(lines)


def render_flatten_json(result: FlattenResult) -> str:
    payload: Dict[str, Any] = {
        "total": len(result.ops),
        "renamed_count": result.changed_count,
        "unchanged_count": result.unchanged_count,
        "ops": [
            {
                "original_key": op.original_key,
                "flat_key": op.flat_key,
                "value": op.value,
                "changed": op.changed,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
