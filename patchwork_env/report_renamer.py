"""Render RenameResult as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.renamer import RenameResult


def render_rename_text(result: RenameResult) -> str:
    lines = ["=== Rename Report ==="]
    lines.append(
        f"renamed: {len(result.renamed)}  "
        f"skipped: {len(result.skipped)}  "
        f"conflicts: {len(result.conflicts)}"
    )
    if result.renamed:
        lines.append("\nRenamed:")
        for op in result.renamed:
            lines.append(f"  {op.old_key!r:30s} -> {op.new_key!r}")
    if result.skipped:
        lines.append("\nSkipped (key not found):")
        for op in result.skipped:
            lines.append(f"  {op.old_key!r}")
    if result.conflicts:
        lines.append("\nConflicts (new key already exists):")
        for op in result.conflicts:
            lines.append(f"  {op.old_key!r} -> {op.new_key!r}")
    return "\n".join(lines)


def render_rename_json(result: RenameResult) -> str:
    return json.dumps(
        {
            "summary": {
                "renamed": len(result.renamed),
                "skipped": len(result.skipped),
                "conflicts": len(result.conflicts),
            },
            "ops": [
                {"old_key": o.old_key, "new_key": o.new_key, "status": o.status}
                for o in result.ops
            ],
        },
        indent=2,
    )
