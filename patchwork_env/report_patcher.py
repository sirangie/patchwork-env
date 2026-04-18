"""Render PatchResult as text or JSON."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.patcher import PatchResult


def render_patch_text(result: PatchResult) -> str:
    lines = ["Patch Report", "============"]
    if not result.ops:
        lines.append("No operations.")
        return "\n".join(lines)

    for op in result.ops:
        if op.action == 'set':
            if op.old_value is None:
                lines.append(f"  + {op.key} = {op.new_value!r}")
            else:
                lines.append(f"  ~ {op.key}: {op.old_value!r} -> {op.new_value!r}")
        elif op.action == 'delete':
            lines.append(f"  - {op.key} (was {op.old_value!r})")
        else:
            lines.append(f"  . {op.key} (skipped)")

    applied = len(result.applied)
    skipped = len(result.skipped)
    lines.append("")
    lines.append(f"Total: {applied} applied, {skipped} skipped")
    return "\n".join(lines)


def render_patch_json(result: PatchResult) -> str:
    payload: Dict[str, Any] = {
        "applied": len(result.applied),
        "skipped": len(result.skipped),
        "ops": [
            {
                "key": op.key,
                "action": op.action,
                "old_value": op.old_value,
                "new_value": op.new_value,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
