"""Render TransformResult as text or JSON."""
import json
from typing import Any, Dict

from patchwork_env.transformer import TransformResult


def render_transform_text(result: TransformResult, show_values: bool = False) -> str:
    lines = ["=== Transform Report ==="]
    lines.append(f"Keys processed : {len(result.ops)}")
    lines.append(f"Changed        : {result.changed_count}")
    lines.append(f"Unchanged      : {result.unchanged_count}")
    lines.append("")

    for op in result.ops:
        if op.changed:
            if show_values:
                lines.append(f"  ~ {op.key}  [{op.transform}]  {op.original!r} -> {op.result!r}")
            else:
                lines.append(f"  ~ {op.key}  [{op.transform}]")
        else:
            lines.append(f"  = {op.key}  (no change)")

    return "\n".join(lines)


def render_transform_json(result: TransformResult) -> str:
    payload: Dict[str, Any] = {
        "changed_count": result.changed_count,
        "unchanged_count": result.unchanged_count,
        "ops": [
            {
                "key": op.key,
                "transform": op.transform,
                "changed": op.changed,
                "original": op.original,
                "result": op.result,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
