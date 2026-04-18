"""Render lint results as text or JSON."""
from __future__ import annotations
import json
from patchwork_env.linter import LintResult


def render_lint_text(result: LintResult) -> str:
    lines = []
    if result.ok:
        lines.append("✔ No lint errors found.")
    else:
        lines.append("✘ Lint errors detected.")
    if result.issues:
        lines.append("")
        for issue in result.issues:
            icon = {"error": "✘", "warning": "⚠", "info": "ℹ"}.get(issue.severity, "•")
            key_part = f" [{issue.key}]" if issue.key else ""
            lines.append(f"  {icon} [{issue.code}]{key_part} line {issue.line}: {issue.message}")
        lines.append("")
        lines.append(
            f"  {len(result.errors)} error(s), {len(result.warnings)} warning(s)"
        )
    return "\n".join(lines)


def render_lint_json(result: LintResult) -> str:
    return json.dumps(
        {
            "ok": result.ok,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "issues": [
                {
                    "line": i.line,
                    "key": i.key,
                    "code": i.code,
                    "message": i.message,
                    "severity": i.severity,
                }
                for i in result.issues
            ],
        },
        indent=2,
    )
