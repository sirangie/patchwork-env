"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax, resolving references within the same env.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')


@dataclass
class InterpolateResult:
    resolved: Dict[str, str]
    unresolved: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unresolved and not self.cycles


def _refs_in(value: str) -> List[str]:
    return [m.group(1) or m.group(2) for m in _REF_RE.finditer(value)]


def _resolve(
    key: str,
    env: Dict[str, str],
    cache: Dict[str, Optional[str]],
    visiting: set,
) -> Optional[str]:
    if key in cache:
        return cache[key]
    if key not in env:
        cache[key] = None
        return None
    if key in visiting:
        return None  # cycle
    visiting.add(key)
    value = env[key]

    def _sub(m: re.Match) -> str:
        ref = m.group(1) or m.group(2)
        resolved = _resolve(ref, env, cache, visiting)
        return resolved if resolved is not None else m.group(0)

    result = _REF_RE.sub(_sub, value)
    visiting.discard(key)
    cache[key] = result
    return result


def interpolate_env(env: Dict[str, str]) -> InterpolateResult:
    """Resolve variable references in *env* and return an InterpolateResult."""
    cache: Dict[str, Optional[str]] = {}
    resolved: Dict[str, str] = {}
    unresolved: List[str] = []
    cycles: List[str] = []

    # detect cycles first via DFS
    def _has_cycle(key: str, visiting: set, visited: set) -> bool:
        if key in visited:
            return False
        if key in visiting:
            return True
        visiting.add(key)
        for ref in _refs_in(env.get(key, "")):
            if ref in env and _has_cycle(ref, visiting, visited):
                return True
        visiting.discard(key)
        visited.add(key)
        return False

    visited: set = set()
    for k in env:
        if _has_cycle(k, set(), visited):
            cycles.append(k)

    for key in env:
        if key in cycles:
            resolved[key] = env[key]
            continue
        value = _resolve(key, env, cache, set())
        if value is None:
            unresolved.append(key)
            resolved[key] = env[key]
        else:
            resolved[key] = value
            refs = _refs_in(env[key])
            for ref in refs:
                if ref not in env:
                    if key not in unresolved:
                        unresolved.append(key)

    return InterpolateResult(resolved=resolved, unresolved=list(set(unresolved)), cycles=cycles)
