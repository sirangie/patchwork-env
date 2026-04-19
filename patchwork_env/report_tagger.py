"""Render TagResult as text or JSON."""
from __future__ import annotations
import json
from typing import List
from patchwork_env.tagger import TagResult


def render_tag_text(result: TagResult, show_values: bool = False) -> str:
    lines: List[str] = ["=== Tag Report ==="]
    lines.append(f"Total keys : {len(result.entries)}")
    lines.append(f"Unique tags: {len(result.all_tags)}")
    lines.append("")

    if result.all_tags:
        for tag in result.all_tags:
            keys = result.keys_for(tag)
            lines.append(f"[{tag}] ({len(keys)} key(s))")
            for k in sorted(keys):
                entry = next(e for e in result.entries if e.key == k)
                if show_values:
                    lines.append(f"  {k}={entry.value}")
                else:
                    lines.append(f"  {k}")
    else:
        lines.append("(no tags defined)")

    untagged = [e.key for e in result.entries if not e.tags]
    if untagged:
        lines.append(f"\n[untagged] ({len(untagged)} key(s))")
        for k in sorted(untagged):
            lines.append(f"  {k}")

    return "\n".join(lines)


def render_tag_json(result: TagResult) -> str:
    return json.dumps(
        {
            "total_keys": len(result.entries),
            "all_tags": result.all_tags,
            "tag_map": result.tag_map,
            "entries": [
                {"key": e.key, "tags": e.tags}
                for e in result.entries
            ],
        },
        indent=2,
    )
