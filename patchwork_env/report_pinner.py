"""Render PinResult as text or JSON."""
import json
from patchwork_env.pinner import PinResult


def render_pin_text(result: PinResult, show_values: bool = False) -> str:
    lines = ["=== Pin Report ==="]
    lines.append(f"Pinned keys : {len(result.entries)}")
    lines.append(f"Blocked     : {result.blocked_count}")
    lines.append("")

    for entry in result.entries:
        if entry.blocked:
            val_part = f" ({entry.attempted_value!r} -> {entry.pinned_value!r})" if show_values else ""
            lines.append(f"  ! {entry.key} [BLOCKED]{val_part}")
        else:
            val_part = f" = {entry.pinned_value!r}" if show_values else ""
            lines.append(f"  * {entry.key} [pinned]{val_part}")

    return "\n".join(lines)


def render_pin_json(result: PinResult) -> str:
    return json.dumps({
        "pinned_count": len(result.entries),
        "blocked_count": result.blocked_count,
        "entries": [
            {
                "key": e.key,
                "pinned_value": e.pinned_value,
                "attempted_value": e.attempted_value,
                "blocked": e.blocked,
            }
            for e in result.entries
        ],
    }, indent=2)
