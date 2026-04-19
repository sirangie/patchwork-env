import json
from typing import Any, Dict
from patchwork_env.normalizer import NormalizeResult


def render_normalize_text(result: NormalizeResult, show_values: bool = False) -> str:
    lines = ["=== Normalize Report ==="]
    lines.append(f"Total keys : {len(result.ops)}")
    lines.append(f"Changed    : {result.changed_count}")
    lines.append(f"Unchanged  : {result.unchanged_count}")
    lines.append("")

    for op in result.ops:
        if op.action == "none":
            prefix = "  "
            detail = op.key
        else:
            prefix = "~ "
            detail = f"{op.key}  [{op.action}]"
            if show_values:
                detail += f"  {op.old_value!r} -> {op.new_value!r}"
        lines.append(f"{prefix}{detail}")

    return "\n".join(lines)


def render_normalize_json(result: NormalizeResult) -> str:
    data: Dict[str, Any] = {
        "total": len(result.ops),
        "changed": result.changed_count,
        "unchanged": result.unchanged_count,
        "ops": [
            {
                "key": op.key,
                "action": op.action,
                "old_value": op.old_value,
                "new_value": op.new_value,
            }
            for op in result.ops
        ],
    }
    return json.dumps(data, indent=2)
