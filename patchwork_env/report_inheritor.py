"""report_inheritor.py — text and JSON rendering for InheritResult."""
from __future__ import annotations
import json
from typing import Any, Dict
from patchwork_env.inheritor import InheritResult


def render_inherit_text(result: InheritResult, show_values: bool = False) -> str:
    lines = ["=== Inherit Report ==="]
    lines.append(
        f"Inherited: {result.inherited_count}  "
        f"Child-only: {result.child_only_count}  "
        f"Overwritten: {result.overwritten_count}"
    )
    lines.append("")

    for op in result.ops:
        if op.source == "parent" and not op.overwritten:
            val_hint = f" = {op.value!r}" if show_values else ""
            lines.append(f"  + {op.key}{val_hint}  (from parent)")
        elif op.overwritten:
            val_hint = f" = {op.value!r}" if show_values else ""
            lines.append(f"  ~ {op.key}{val_hint}  (overwritten by parent)")
        else:
            val_hint = f" = {op.value!r}" if show_values else ""
            lines.append(f"    {op.key}{val_hint}  (child)")

    return "\n".join(lines)


def render_inherit_json(result: InheritResult) -> str:
    payload: Dict[str, Any] = {
        "inherited_count": result.inherited_count,
        "child_only_count": result.child_only_count,
        "overwritten_count": result.overwritten_count,
        "ops": [
            {
                "key": op.key,
                "source": op.source,
                "overwritten": op.overwritten,
            }
            for op in result.ops
        ],
    }
    return json.dumps(payload, indent=2)
