"""Parser for .env files — handles reading and tokenizing key-value pairs."""

import re
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_RE = re.compile(r'^\s*#')


def parse_env_file(path: str) -> Dict[str, str]:
    """Read a .env file and return a dict of key -> value pairs.

    - Strips inline comments (values ending with  # ...)
    - Strips surrounding quotes from values
    - Skips blank lines and comment lines
    """
    env: Dict[str, str] = {}

    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')

            if not line.strip() or COMMENT_RE.match(line):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                continue

            key = match.group('key')
            value = _clean_value(match.group('value'))
            env[key] = value

    return env


def _clean_value(raw: str) -> str:
    """Strip quotes and inline comments from a raw env value."""
    raw = raw.strip()

    # Remove surrounding quotes (single or double)
    if len(raw) >= 2 and raw[0] in ('"', "'") and raw[-1] == raw[0]:
        return raw[1:-1]

    # Strip inline comment (space + # ...)
    raw = re.sub(r'\s+#.*$', '', raw)
    return raw


def serialize_env(env: Dict[str, str]) -> str:
    """Serialize a dict back to .env file content."""
    lines = [f'{k}={_quote_if_needed(v)}' for k, v in sorted(env.items())]
    return '\n'.join(lines) + '\n'


def _quote_if_needed(value: str) -> str:
    """Wrap value in double quotes if it contains spaces or special chars."""
    if re.search(r'[\s#"\']', value):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value
