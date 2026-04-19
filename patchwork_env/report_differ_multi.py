"""Render multi-env diff results as text or JSON."""
import json
from typing import List
from .differ_multi import MultiDiffResult

_STATUS_SYMBOL = {
    "unchanged": "=",
    "changed": "~",
    "added": "+",
    "removed": "-",
}


def render_multi_text(result: MultiDiffResult, show_unchanged: bool = False) -> str:
    lines: List[str] = []
    lines.append(f"Multi-Diff (base: {result.base_label})")
    lines.append("=" * 40)
    for label in result.labels():
        lines.append(f"\n[{label}]")
        entries = result.for_env(label)
        shown = 0
        for e in entries:
            if e.status == "unchanged" and not show_unchanged:
                continue
            sym = _STATUS_SYMBOL.get(e.status, "?")
            if e.status == "changed":
                lines.append(f"  {sym} {e.key}: {e.old_value!r} -> {e.new_value!r}")
            elif e.status == "added":
                lines.append(f"  {sym} {e.key}: {e.new_value!r}")
            elif e.status == "removed":
                lines.append(f"  {sym} {e.key}: {e.old_value!r}")
            shown += 1
        if shown == 0:
            lines.append("  (no differences)")
    lines.append("")
    summary = result.summary()
    lines.append("Summary:")
    for label, counts in summary.items():
        parts = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        lines.append(f"  {label}: {parts}")
    return "\n".join(lines)


def render_multi_json(result: MultiDiffResult) -> str:
    payload = {
        "base": result.base_label,
        "summary": result.summary(),
        "diffs": {
            label: [
                {
                    "key": e.key,
                    "status": e.status,
                    "old_value": e.old_value,
                    "new_value": e.new_value,
                }
                for e in entries
            ]
            for label, entries in result.results.items()
        },
    }
    return json.dumps(payload, indent=2)
