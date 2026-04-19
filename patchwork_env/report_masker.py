"""report_masker.py — Text and JSON rendering for MaskResult."""
from __future__ import annotations
import json
from patchwork_env.masker import MaskResult, PLACEHOLDER


def render_mask_text(result: MaskResult, *, show_values: bool = False) -> str:
    lines = ["=== Mask Report ==="]
    lines.append(f"Total keys : {len(result.ops)}")
    lines.append(f"Masked     : {result.masked_count}")
    lines.append(f"Kept       : {result.kept_count}")
    lines.append("")

    for op in result.ops:
        if op.masked:
            prefix = "[M]"
            display = PLACEHOLDER
        else:
            prefix = "[ ]"
            display = op.original if show_values else "<kept>"
        reason = f"  # {op.reason}" if op.reason else ""
        lines.append(f"  {prefix} {op.key} = {display}{reason}")

    return "\n".join(lines)


def render_mask_json(result: MaskResult) -> str:
    payload = {
        "total": len(result.ops),
        "masked_count": result.masked_count,
        "kept_count": result.kept_count,
        "masked_keys": result.masked_keys,
        "env": result.env,
    }
    return json.dumps(payload, indent=2)
