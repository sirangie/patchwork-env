"""Lint .env files for common style and correctness issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class LintIssue:
    line: int
    key: str | None
    code: str
    message: str
    severity: str  # "error" | "warning" | "info"

    def __repr__(self) -> str:
        loc = f"line {self.line}" if self.line else "?"
        k = f" [{self.key}]" if self.key else ""
        return f"{self.severity.upper()} {self.code}{k} @ {loc}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_CHECKS = []


def _check(fn):
    _CHECKS.append(fn)
    return fn


@_check
def _check_no_spaces_around_equals(lines: List[str], issues: List[LintIssue]):
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if " = " in stripped or stripped.startswith("= ") or " =" in stripped.split("=")[0]:
            key = stripped.split("=")[0].strip()
            issues.append(LintIssue(i, key, "E001", "spaces around '=' sign", "error"))


@_check
def _check_no_bare_keys(lines: List[str], issues: List[LintIssue]):
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if "=" not in stripped:
            issues.append(LintIssue(i, None, "E002", f"line has no '=': {stripped!r}", "error"))


@_check
def _check_duplicate_keys(lines: List[str], issues: List[LintIssue]):
    seen: Dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped or "=" not in stripped:
            continue
        key = stripped.split("=")[0].strip()
        if key in seen:
            issues.append(LintIssue(i, key, "W001", f"duplicate key (first at line {seen[key]})", "warning"))
        else:
            seen[key] = i


@_check
def _check_empty_values(lines: List[str], issues: List[LintIssue]):
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        if not val.strip():
            issues.append(LintIssue(i, key.strip(), "W002", "empty value", "warning"))


def lint_env(source: str) -> LintResult:
    lines = source.splitlines()
    issues: List[LintIssue] = []
    for check in _CHECKS:
        check(lines, issues)
    issues.sort(key=lambda x: x.line)
    return LintResult(issues=issues)
