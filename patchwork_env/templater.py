"""Generate .env.template files from existing .env files, stripping secret values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse_env_file

# Keys whose values are kept as-is (non-secret defaults)
_SAFE_PATTERNS = ("ENV", "APP_ENV", "DEBUG", "LOG_LEVEL", "PORT", "HOST", "TZ")


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    original_value: Optional[str] = None
    kept: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        return f"TemplateEntry({self.key!r}, kept={self.kept})"


def _is_safe_key(key: str) -> bool:
    return any(key == pat or key.endswith(f"_{pat}") for pat in _SAFE_PATTERNS)


def build_template(
    env_path: str,
    keep_safe: bool = True,
    placeholder: str = "",
) -> List[TemplateEntry]:
    """Parse an env file and return template entries with values masked."""
    pairs = parse_env_file(env_path)
    entries: List[TemplateEntry] = []
    for key, value in pairs.items():
        safe = keep_safe and _is_safe_key(key)
        entries.append(
            TemplateEntry(
                key=key,
                placeholder=value if safe else placeholder,
                original_value=value,
                kept=safe,
            )
        )
    return entries


def serialize_template(entries: List[TemplateEntry]) -> str:
    """Render template entries to a .env.template string."""
    lines: List[str] = []
    for e in entries:
        lines.append(f"{e.key}={e.placeholder}")
    return "\n".join(lines) + ("\n" if lines else "")


def write_template(entries: List[TemplateEntry], dest: str) -> None:
    """Write rendered template to *dest*."""
    with open(dest, "w") as fh:
        fh.write(serialize_template(entries))
