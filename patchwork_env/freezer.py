"""freezer.py — freeze an env dict to a locked snapshot that rejects changes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeViolation:
    key: str
    expected: str
    actual: Optional[str]  # None means key was removed

    def __repr__(self) -> str:
        return f"FreezeViolation(key={self.key!r}, expected={self.expected!r}, actual={self.actual!r})"


@dataclass
class FreezeResult:
    frozen: Dict[str, str]
    violations: List[FreezeViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def violated_keys(self) -> List[str]:
        return [v.key for v in self.violations]


def freeze_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a frozen copy of the env dict."""
    return dict(env)


def check_frozen(
    frozen: Dict[str, str],
    current: Dict[str, str],
    strict: bool = False,
) -> FreezeResult:
    """
    Compare current env against a frozen baseline.

    strict=True also flags keys added in current that weren't in frozen.
    """
    violations: List[FreezeViolation] = []

    for key, expected in frozen.items():
        actual = current.get(key)
        if actual != expected:
            violations.append(FreezeViolation(key=key, expected=expected, actual=actual))

    if strict:
        for key in current:
            if key not in frozen:
                violations.append(FreezeViolation(key=key, expected="<absent>", actual=current[key]))

    return FreezeResult(frozen=frozen, violations=violations)
