"""Render GroupResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.grouper import GroupResult


def render_group_text(result: GroupResult, show_values: bool = False) -> str:
    lines = ["=== Key Groups ==="]
    lines.append(f"Total keys : {result.total_keys}")
    lines.append(f"Groups     : {len(result.groups)}")
    lines.append(f"Ungrouped  : {len(result.ungrouped)}")
    lines.append("")

    for group in result.group_names:
        keys = result.keys_in(group)
        lines.append(f"[{group}]  ({len(keys)} keys)")
        for key in keys:
            if show_values:
                val = result.groups[group][key]
                lines.append(f"  {key} = {val}")
            else:
                lines.append(f"  {key}")
        lines.append("")

    if result.ungrouped:
        lines.append("[ungrouped]")
        for key in sorted(result.ungrouped):
            if show_values:
                lines.append(f"  {key} = {result.ungrouped[key]}")
            else:
                lines.append(f"  {key}")

    return "\n".join(lines)


def render_group_json(result: GroupResult) -> str:
    payload = {
        "total_keys": result.total_keys,
        "group_count": len(result.groups),
        "ungrouped_count": len(result.ungrouped),
        "groups": {g: result.keys_in(g) for g in result.group_names},
        "ungrouped": sorted(result.ungrouped.keys()),
    }
    return json.dumps(payload, indent=2)
