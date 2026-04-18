"""Render export results for CLI output."""
from __future__ import annotations
import json
from typing import Dict


def render_export_text(env: Dict[str, str], fmt: str, content: str) -> str:
    """Wrap exported content with a small header for CLI display."""
    count = len(env)
    lines = [
        f"# patchwork-env export  format={fmt}  keys={count}",
        "",
        content.rstrip(),
        "",
    ]
    return "\n".join(lines)


def render_export_json(env: Dict[str, str], fmt: str, content: str) -> str:
    """Return a JSON wrapper with metadata + the exported payload."""
    payload: dict = {
        "format": fmt,
        "key_count": len(env),
        "output": content,
    }
    return json.dumps(payload, indent=2) + "\n"
