"""Render ScoreResult as text or JSON."""
import json
from patchwork_env.scorer import ScoreResult


def render_score_text(result: ScoreResult) -> str:
    lines = [
        "=== Env Health Score ===",
        f"  Overall : {result.total}/100  (Grade {result.grade()})",
        f"  Lint    : {result.lint_score}/40",
        f"  Profile : {result.profile_score}/30",
    ]
    if result.validation_score is not None:
        lines.append(f"  Validate: {result.validation_score}/30")
    else:
        lines.append("  Validate: N/A (no schema)")
    lines.append("")
    lines.append(result.summary)
    return "\n".join(lines)


def render_score_json(result: ScoreResult) -> str:
    data = {
        "total": result.total,
        "grade": result.grade(),
        "lint_score": result.lint_score,
        "profile_score": result.profile_score,
        "validation_score": result.validation_score,
        "summary": result.summary,
    }
    return json.dumps(data, indent=2)
