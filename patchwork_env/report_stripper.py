"""report_stripper.py — render StripResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.stripper import StripResult


def render_strip_text(result: StripResult) -> str:
    lines = ["=== Strip Report ==="]
    lines.append(f"Total keys before : {len(result.original)}")
    lines.append(f"Keys removed      : {result.removed_count}")
    lines.append(f"Keys remaining    : {len(result.stripped)}")
    if result.ops:
        lines.append("")
        lines.append("Removed:")
        for op in result.ops:
            lines.append(f"  - {op.key}  [{op.reason}]")
    else:
        lines.append("No keys removed.")
    return "\n".join(lines)


def render_strip_json(result: StripResult) -> str:
    payload = {
        "total_before": len(result.original),
        "removed_count": result.removed_count,
        "remaining_count": len(result.stripped),
        "removed": [
            {"key": op.key, "reason": op.reason} for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
