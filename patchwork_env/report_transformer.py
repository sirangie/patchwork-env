"""Render TransformResult as text or JSON."""
import json
from typing import Any, Dict

from patchwork_env.transformer import TransformResult


def render_transform_text(result: TransformResult, show_values: bool = False) -> str:
    """Render a TransformResult as a human-readable text report.

    Args:
        result: The TransformResult to render.
        show_values: If True, include original and transformed values in the output.

    Returns:
        A formatted multi-line string report.
    """
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
    """Render a TransformResult as a JSON string.

    Args:
        result: The TransformResult to render.

    Returns:
        A JSON-formatted string representation of the result.
    """
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


def render_transform_summary(result: TransformResult) -> str:
    """Return a compact one-line summary of a TransformResult.

    Useful for logging or CLI status lines.

    Args:
        result: The TransformResult to summarise.

    Returns:
        A single-line summary string, e.g. "3 keys processed: 2 changed, 1 unchanged".
    """
    total = len(result.ops)
    return (
        f"{total} key{'s' if total != 1 else ''} processed: "
        f"{result.changed_count} changed, {result.unchanged_count} unchanged"
    )
