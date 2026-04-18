"""Render SortResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.sorter import SortResult


def render_sort_text(result: SortResult, *, show_values: bool = False) -> str:
    lines = ["=== Sort Result ==="]
    lines.append(f"Total keys : {len(result.sorted_order)}")
    lines.append(f"Keys moved : {result.moved}")

    if result.groups:
        lines.append("")
        lines.append("Groups:")
        for prefix, keys in result.groups.items():
            lines.append(f"  [{prefix}*] -> {len(keys)} key(s)")

    lines.append("")
    lines.append("Sorted order:")
    for key in result.sorted_order:
        if show_values:
            lines.append(f"  {key}={result.env[key]}")
        else:
            lines.append(f"  {key}")

    return "\n".join(lines)


def render_sort_json(result: SortResult) -> str:
    payload = {
        "total": len(result.sorted_order),
        "moved": result.moved,
        "original_order": result.original_order,
        "sorted_order": result.sorted_order,
        "groups": {p: keys for p, keys in result.groups.items()},
    }
    return json.dumps(payload, indent=2)
