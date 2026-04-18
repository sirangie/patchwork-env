"""Export parsed env data to various formats (shell, docker, json)."""
from __future__ import annotations
import json
import shlex
from typing import Dict


SUPPORTED_FORMATS = ("shell", "docker", "json")


def export_env(env: Dict[str, str], fmt: str) -> str:
    """Serialize *env* dict to the requested export format."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format {fmt!r}. Choose from {SUPPORTED_FORMATS}")
    if fmt == "shell":
        return _to_shell(env)
    if fmt == "docker":
        return _to_docker(env)
    if fmt == "json":
        return _to_json(env)


def _to_shell(env: Dict[str, str]) -> str:
    """export KEY=VALUE lines suitable for sourcing in bash."""
    lines = []
    for key, value in sorted(env.items()):
        quoted = shlex.quote(value)
        lines.append(f"export {key}={quoted}")
    return "\n".join(lines) + ("\n" if lines else "")


def _to_docker(env: Dict[str, str]) -> str:
    """KEY=VALUE lines suitable for docker --env-file."""
    lines = []
    for key, value in sorted(env.items()):
        # docker env-file does not support quoting — values are literal
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def _to_json(env: Dict[str, str]) -> str:
    return json.dumps(env, indent=2, sort_keys=True) + "\n"
