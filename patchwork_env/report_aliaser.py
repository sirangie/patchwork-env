"""report_aliaser.py – text and JSON rendering for AliasResult."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.aliaser import AliasResult


def render_alias_text(result: AliasResult, show_values: bool = False) -> str:
    lines = ["=== Alias Report ==="]
    lines.append(f"Aliased : {result.aliased_count}")
    lines.append(f"Skipped : {result.skipped_count}")
    lines.append("")

    for op in result.ops:
        if op.skipped:
            lines.append(f"  SKIP  {op.original_key} -> {op.alias_key}  ({op.reason})")
        else:
            value_part = f"  = {op.value!r}" if show_values else ""
            lines.append(f"  ->    {op.original_key} -> {op.alias_key}{value_part}")

    return "\n".join(lines)


def render_alias_json(result: AliasResult) -> str:
    payload: Dict[str, Any] = {
        "aliased_count": result.aliased_count,
        "skipped_count": result.skipped_count,
        "aliased_keys": result.aliased_keys,
        "ops": [
            {
                "original_key": op.original_key,
                "alias_key": op.alias_key,
                "skipped": op.skipped,
                "reason": op.reason,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
