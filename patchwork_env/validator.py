"""Validate .env files against a schema/template."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationIssue:
    key: str
    severity: str  # 'error' | 'warning'
    message: str

    def __repr__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_env(
    env: dict[str, str],
    template: dict[str, str],
    *,
    allow_extra: bool = True,
) -> ValidationResult:
    """Validate *env* against *template*.

    Keys present in template with a non-empty value are treated as required.
    Keys with an empty template value are optional (warning if missing).
    """
    result = ValidationResult()

    for key, tmpl_val in template.items():
        if key not in env:
            if tmpl_val.strip():  # non-empty template value => required
                result.issues.append(
                    ValidationIssue(key, "error", "required key is missing")
                )
            else:
                result.issues.append(
                    ValidationIssue(key, "warning", "optional key is missing")
                )
        elif not env[key].strip():
            result.issues.append(
                ValidationIssue(key, "warning", "key is present but empty")
            )

    if not allow_extra:
        for key in env:
            if key not in template:
                result.issues.append(
                    ValidationIssue(key, "warning", "extra key not in template")
                )

    return result
