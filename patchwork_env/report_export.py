"""Render export results as text or JSON."""
from __future__ import annotations
import json
from typing import Dict


def render_export_text(env: Dict[str, str], fmt: str) -> str:
    """Return a human-readable summary of an export operation."""
    lines = [
        f"Export format : {fmt}",
        f"Keys exported : {len(env)}",
        "",
    ]
    for key in sorted(env):
        lines.append(f"  {key}")
    return "\n".join(lines)


def render_export_json(env: Dict[str, str], fmt: str) -> str:
    """Return a JSON summary of an export operation (values are NOT included)."""
    payload = {
        "format": fmt,
        "key_count": len(env),
        "keys": sorted(env.keys()),
    }
    return json.dumps(payload, indent=2)
