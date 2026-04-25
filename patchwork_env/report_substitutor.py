"""report_substitutor.py – text and JSON renderers for SubstituteResult."""
from __future__ import annotations

import json
from typing import Any, Dict

from .substitutor import SubstituteResult


def render_substitute_text(result: SubstituteResult, *, show_values: bool = False) -> str:
    lines = ["=== Substitutor Report ==="]
    lines.append(
        f"Substituted: {result.substituted_count}  Unchanged: {result.unchanged_count}  "
        f"Total: {len(result.env)}"
    )
    if not result.ops:
        lines.append("(no substitutions made)")
    else:
        lines.append("")
        for op in result.ops:
            if show_values:
                lines.append(f"  ~ {op.key}: {op.old_value!r} -> {op.new_value!r}")
            else:
                lines.append(f"  ~ {op.key}")
    return "\n".join(lines)


def render_substitute_json(result: SubstituteResult) -> str:
    payload: Dict[str, Any] = {
        "substituted_count": result.substituted_count,
        "unchanged_count": result.unchanged_count,
        "total": len(result.env),
        "substitutions": [
            {
                "key": op.key,
                "old_value": op.old_value,
                "new_value": op.new_value,
                "placeholder": op.placeholder,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
