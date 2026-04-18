"""Render FilterResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.filter import FilterResult


def render_filter_text(result: FilterResult, show_values: bool = False) -> str:
    lines = ["Filter Results", "=============="]
    lines.append(f"Matched : {result.count}")
    lines.append(f"Excluded: {result.excluded_count}")

    if result.matched:
        lines.append("\nMatched keys:")
        for k, v in sorted(result.matched.items()):
            val_part = f" = {v}" if show_values else ""
            lines.append(f"  {k}{val_part}")

    if result.excluded:
        lines.append("\nExcluded keys:")
        for k in sorted(result.excluded):
            lines.append(f"  {k}")

    return "\n".join(lines)


def render_filter_json(result: FilterResult) -> str:
    return json.dumps(
        {
            "matched": result.matched,
            "excluded": result.excluded,
            "stats": {
                "matched": result.count,
                "excluded": result.excluded_count,
            },
        },
        indent=2,
    )
