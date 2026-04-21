"""Render DedupeResult as text or JSON."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.deduplicator import DedupeResult


def render_dedupe_text(result: DedupeResult, show_values: bool = False) -> str:
    lines = ["=== Deduplication Report ==="]
    if result.clean:
        lines.append("No duplicate keys found.")
        return "\n".join(lines)

    lines.append(f"Duplicates resolved: {result.deduplicated_count}")
    lines.append("")
    for op in result.ops:
        lines.append(f"  ~ {op.key}  [strategy={op.strategy}]")
        if show_values:
            lines.append(f"      kept:    {op.kept_value!r}")
            for d in op.dropped_values:
                lines.append(f"      dropped: {d!r}")
    return "\n".join(lines)


def render_dedupe_json(result: DedupeResult) -> str:
    data: Dict[str, Any] = {
        "clean": result.clean,
        "deduplicated_count": result.deduplicated_count,
        "ops": [
            {
                "key": op.key,
                "kept_value": op.kept_value,
                "dropped_values": op.dropped_values,
                "strategy": op.strategy,
            }
            for op in result.ops
        ],
        "env": result.env,
    }
    return json.dumps(data, indent=2)
