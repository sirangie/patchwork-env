"""report_rotator.py — text and JSON renderers for RotateResult."""
from __future__ import annotations

import json
from typing import Any, Dict

from patchwork_env.rotator import RotateResult


def render_rotate_text(result: RotateResult) -> str:
    lines = ["=== Rotation Check ==="]
    lines.append(
        f"Threshold : {result.threshold_days} days"
    )
    lines.append(
        f"Keys checked : {len(result.entries)} "
        f"| Due: {result.due_count} | OK: {result.ok_count}"
    )

    if result.clean:
        lines.append("\nAll secret keys are within rotation policy.")
    else:
        lines.append("\nKeys requiring rotation:")
        for entry in result.entries:
            if entry.due:
                age_str = (
                    f"{entry.age_days:.1f}d"
                    if entry.age_days is not None
                    else "unknown age"
                )
                lines.append(f"  ! {entry.key:<30}  ({age_str})  {entry.reason}")

    lines.append("\nAll entries:")
    for entry in result.entries:
        marker = "!" if entry.due else " "
        age_str = (
            f"{entry.age_days:.1f}d" if entry.age_days is not None else "n/a"
        )
        lines.append(f"  [{marker}] {entry.key:<30}  age={age_str}")

    return "\n".join(lines)


def render_rotate_json(result: RotateResult) -> str:
    payload: Dict[str, Any] = {
        "threshold_days": result.threshold_days,
        "clean": result.clean,
        "due_count": result.due_count,
        "ok_count": result.ok_count,
        "due_keys": result.due_keys,
        "entries": [
            {
                "key": e.key,
                "last_rotated": e.last_rotated,
                "age_days": round(e.age_days, 2) if e.age_days is not None else None,
                "due": e.due,
                "reason": e.reason,
            }
            for e in result.entries
        ],
    }
    return json.dumps(payload, indent=2)
