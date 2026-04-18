"""Score an env file for overall health based on lint, profile, and validation results."""
from dataclasses import dataclass
from typing import Optional
from patchwork_env.profiler import ProfileResult
from patchwork_env.linter import LintResult
from patchwork_env.validator import ValidationResult


@dataclass
class ScoreResult:
    total: int  # 0-100
    lint_score: int
    profile_score: int
    validation_score: Optional[int]  # None if no schema provided
    summary: str

    def grade(self) -> str:
        if self.total >= 90:
            return "A"
        elif self.total >= 75:
            return "B"
        elif self.total >= 60:
            return "C"
        elif self.total >= 40:
            return "D"
        return "F"


def score_env(
    lint: LintResult,
    profile: ProfileResult,
    validation: Optional[ValidationResult] = None,
) -> ScoreResult:
    # Lint score: start at 40, deduct per issue
    lint_score = 40
    for issue in lint.issues:
        if issue.level == "error":
            lint_score -= 8
        else:
            lint_score -= 3
    lint_score = max(0, min(40, lint_score))

    # Profile score: up to 30 pts — penalise empty values
    profile_score = 30
    if profile.total > 0:
        empty_ratio = profile.empty_count / profile.total
        profile_score = int(30 * (1 - empty_ratio))
    profile_score = max(0, min(30, profile_score))

    # Validation score: up to 30 pts
    if validation is None:
        validation_score = None
        val_pts = 30  # give full benefit of the doubt
    else:
        val_pts = 30
        for issue in validation.issues:
            if issue.level == "error":
                val_pts -= 10
            else:
                val_pts -= 4
        val_pts = max(0, min(30, val_pts))
        validation_score = val_pts

    total = lint_score + profile_score + (validation_score if validation_score is not None else val_pts)
    total = max(0, min(100, total))

    result = ScoreResult(
        total=total,
        lint_score=lint_score,
        profile_score=profile_score,
        validation_score=validation_score,
        summary=f"Grade {ScoreResult(total, lint_score, profile_score, validation_score, '').grade()}: lint={lint_score}/40 profile={profile_score}/30 validation={validation_score if validation_score is not None else 'N/A'}/30",
    )
    return result
