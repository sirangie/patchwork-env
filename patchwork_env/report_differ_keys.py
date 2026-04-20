"""Renderers for KeyDiffResult."""
from __future__ import annotations
import json
from patchwork_env.differ_keys import KeyDiffResult


def render_key_diff_text(result: KeyDiffResult, *, show_shared: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Key-set diff: {result.base_label!r} vs {result.target_label!r}")
    lines.append(
        f"  Base keys: {len(result.base_keys)}  "
        f"Target keys: {len(result.target_keys)}  "
        f"Shared: {len(result.shared)}  "
        f"Coverage: {result.coverage:.0%}"
    )

    if result.only_in_base:
        lines.append(f"\nOnly in {result.base_label!r} ({len(result.only_in_base)}):")
        for k in result.only_in_base:
            lines.append(f"  - {k}")

    if result.only_in_target:
        lines.append(f"\nOnly in {result.target_label!r} ({len(result.only_in_target)}):")
        for k in result.only_in_target:
            lines.append(f"  + {k}")

    if show_shared and result.shared:
        lines.append(f"\nShared ({len(result.shared)}):")
        for k in result.shared:
            lines.append(f"  = {k}")

    if not result.has_differences:
        lines.append("\nNo key-set differences found.")

    return "\n".join(lines)


def render_key_diff_json(result: KeyDiffResult) -> str:
    data = {
        "base_label": result.base_label,
        "target_label": result.target_label,
        "base_key_count": len(result.base_keys),
        "target_key_count": len(result.target_keys),
        "shared_count": len(result.shared),
        "coverage": round(result.coverage, 4),
        "only_in_base": result.only_in_base,
        "only_in_target": result.only_in_target,
        "shared": result.shared,
        "has_differences": result.has_differences,
    }
    return json.dumps(data, indent=2)
