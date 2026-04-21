"""Render AliasResult as human-readable text or JSON."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from patchwork_env.aliaser import AliasResult


def render_alias_text(result: "AliasResult", show_values: bool = False) -> str:
    """Return a plain-text summary of the alias operation."""
    lines: list[str] = []
    lines.append("=== Alias Report ===")
    lines.append(
        f"Keys aliased : {result.aliased_count}"
    )
    lines.append(
        f"Keys skipped : {result.skipped_count}"
    )
    lines.append("")

    if not result.ops:
        lines.append("(no operations recorded)")
        return "\n".join(lines)

    for op in result.ops:
        if op.action == "aliased":
            if show_values:
                lines.append(
                    f"  [aliased]  {op.original_key} -> {op.alias_key}  "
                    f"value={op.value!r}"
                )
            else:
                lines.append(
                    f"  [aliased]  {op.original_key} -> {op.alias_key}"
                )
ipped":
            lines.append(
                f"  [skipped]  {op.original_key} -> {op.alias_key}  "
                f"reason={op.reason or 'n/a'}"
            )
        else:
            lines[{op.action}]  {op.original_key} -> {op.alias_key}"
            )

    return "\n".join(lines)


def render_alias_json(result: "AliasResult") -> str JSON string representation of the alias result."""
    payload = {
        "aliased_count": result.aliased_count,
        "skipped_count": result.skipped_count,
        "env": result.env,
        "ops": [
            {
                "action": op.action,
                "original_key": op.original_key,
                "alias_key": op.alias_key,
                "value":reason": op.reason,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
