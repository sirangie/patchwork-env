"""report_freezer.py — render FreezeResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.freezer import FreezeResult


def render_freeze_text(result: FreezeResult, *, show_values: bool = False) -> str:
    lines = ["=== Freeze Check ==="]
    lines.append(f"Frozen keys : {len(result.frozen)}")
    lines.append(f"Violations  : {result.violation_count}")
    lines.append(f"Status      : {'OK' if result.ok else 'VIOLATIONS FOUND'}")

    if result.violations:
        lines.append("")
        lines.append("Violations:")
        for v in result.violations:
            if v.actual is None:
                tag = "REMOVED"
            elif v.expected == "<absent>":
                tag = "ADDED"
            else:
                tag = "CHANGED"
            if show_values:
                lines.append(f"  [{tag}] {v.key}  expected={v.expected!r}  actual={v.actual!r}")
            else:
                lines.append(f"  [{tag}] {v.key}")

    return "\n".join(lines)


def render_freeze_json(result: FreezeResult) -> str:
    payload = {
        "ok": result.ok,
        "frozen_key_count": len(result.frozen),
        "violation_count": result.violation_count,
        "violations": [
            {"key": v.key, "expected": v.expected, "actual": v.actual}
            for v in result.violations
        ],
    }
    return json.dumps(payload, indent=2)
