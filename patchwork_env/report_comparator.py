"""Render comparison results as text or JSON."""
import json
from patchwork_env.comparator import CompareResult


def render_compare_text(result: CompareResult) -> str:
    lines = [
        f"Comparing {result.left_label!r} vs {result.right_label!r}",
        "-" * 48,
    ]
    if result.is_identical:
        lines.append("Files are identical.")
        return "\n".join(lines)

    for e in result.added:
        lines.append(f"  + {e.key} (only in {result.right_label})")
    for e in result.removed:
        lines.append(f"  - {e.key} (only in {result.left_label})")
    for e in result.changed:
        lines.append(f"  ~ {e.key} (value differs)")

    lines.append("")
    lines.append(
        f"Summary: {len(result.added)} added, {len(result.removed)} removed, "
        f"{len(result.changed)} changed, {len(result.same)} same"
    )
    return "\n".join(lines)


def render_compare_json(result: CompareResult) -> str:
    data = {
        "left_label": result.left_label,
        "right_label": result.right_label,
        "identical": result.is_identical,
        "summary": {
            "added": len(result.added),
            "removed": len(result.removed),
            "changed": len(result.changed),
            "same": len(result.same),
        },
        "entries": [
            {"key": e.key, "status": e.status}
            for e in result.entries
        ],
    }
    return json.dumps(data, indent=2)
