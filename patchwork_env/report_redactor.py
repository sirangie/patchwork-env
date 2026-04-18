"""Render redaction results as text or JSON."""
from __future__ import annotations

import json
from typing import Any, Dict

from .redactor import RedactResult


def render_redact_text(result: RedactResult) -> str:
    lines = ["Redaction Report", "================"]
    lines.append(f"Total keys : {len(result.original)}")
    lines.append(f"Redacted   : {result.count}")
    if result.redacted_keys:
        lines.append("\nRedacted keys:")
        for k in result.redacted_keys:
            lines.append(f"  - {k}")
    else:
        lines.append("\nNo keys were redacted.")
    lines.append("\nSafe output:")
    for k, v in result.redacted.items():
        lines.append(f"  {k}={v}")
    return "\n".join(lines)


def render_redact_json(result: RedactResult) -> str:
    payload: Dict[str, Any] = {
        "total": len(result.original),
        "redacted_count": result.count,
        "redacted_keys": result.redacted_keys,
        "env": result.redacted,
    }
    return json.dumps(payload, indent=2)
