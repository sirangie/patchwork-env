"""Rendering helpers for CoerceResult — text and JSON output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from patchwork_env.coercer import CoerceResult


def render_coerce_text(result: "CoerceResult", show_values: bool = False) -> str:
    """Return a human-readable summary of a coercion run.

    Args:
        result: The CoerceResult produced by coerce_env().
        show_values: When True, print the before/after value alongside each op.
    """
    lines: list[str] = []
    lines.append("=== Coercion Report ===")
    lines.append(
        f"Total keys: {result.total}  "
        f"success: {result.success_count}  "
        f"failed: {result.failure_count}  "
        f"skipped: {result.skipped_count}"
    )

    if not result.ops:
        lines.append("(no operations performed)")
        return "\n".join(lines)

    lines.append("")

    # Group by outcome for readability
    successes = [op for op in result.ops if op.status == "coerced"]
    failures  = [op for op in result.ops if op.status == "failed"]
    skipped   = [op for op in result.ops if op.status == "skipped"]

    if successes:
        lines.append("Coerced:")
        for op in successes:
            tag = f"  ~ {op.key}  ({op.from_type} -> {op.to_type})"
            if show_values:
                tag += f"  [{op.original!r} => {op.coerced!r}]"
            lines.append(tag)

    if failures:
        lines.append("Failed:")
        for op in failures:
            tag = f"  ! {op.key}  ({op.from_type} -> {op.to_type})"
            if show_values:
                tag += f"  [{op.original!r}]"
            if op.error:
                tag += f"  error: {op.error}"
            lines.append(tag)

    if skipped:
        lines.append("Skipped:")
        for op in skipped:
            lines.append(f"  - {op.key}")

    return "\n".join(lines)


def render_coerce_json(result: "CoerceResult") -> str:
    """Return a JSON string representation of the coercion result."""
    payload = {
        "total": result.total,
        "success_count": result.success_count,
        "failure_count": result.failure_count,
        "skipped_count": result.skipped_count,
        "ops": [
            {
                "key": op.key,
                "status": op.status,
                "from_type": op.from_type,
                "to_type": op.to_type,
                "original": op.original,
                "coerced": op.coerced,
                "error": op.error,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
