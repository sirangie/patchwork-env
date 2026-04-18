"""Render diff results to human-readable text or structured output."""

from typing import List
from patchwork_env.differ import DiffEntry, summary

ANSI = {
    'added':     '\033[32m',  # green
    'removed':   '\033[31m',  # red
    'changed':   '\033[33m',  # yellow
    'unchanged': '\033[90m',  # dark grey
    'reset':     '\033[0m',
}

PREFIX = {
    'added': '+',
    'removed': '-',
    'changed': '~',
    'unchanged': ' ',
}


def render_text(entries: List[DiffEntry], color: bool = True, show_unchanged: bool = False) -> str:
    lines = []
    for e in entries:
        if e.status == 'unchanged' and not show_unchanged:
            continue

        prefix = PREFIX[e.status]

        if e.status == 'changed':
            line = f"{prefix} {e.key}: {e.left_value!r} -> {e.right_value!r}"
        elif e.status == 'added':
            line = f"{prefix} {e.key}={e.right_value}"
        elif e.status == 'removed':
            line = f"{prefix} {e.key}={e.left_value}"
        else:
            line = f"{prefix} {e.key}={e.left_value}"

        if color:
            line = f"{ANSI[e.status]}{line}{ANSI['reset']}"

        lines.append(line)

    return '\n'.join(lines)


def render_summary(entries: List[DiffEntry], color: bool = True) -> str:
    s = summary(entries)
    parts = [
        f"+{s['added']} added",
        f"-{s['removed']} removed",
        f"~{s['changed']} changed",
        f" {s['unchanged']} unchanged",
    ]
    line = '  '.join(parts)
    if color:
        line = f"\033[1m{line}{ANSI['reset']}"
    return line


def render_json(entries: List[DiffEntry]) -> list:
    return [
        {
            'key': e.key,
            'status': e.status,
            'left': e.left_value,
            'right': e.right_value,
        }
        for e in entries
    ]
