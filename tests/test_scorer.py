import pytest
from patchwork_env.scorer import score_env, ScoreResult
from patchwork_env.linter import LintResult, LintIssue
from patchwork_env.profiler import ProfileResult
from patchwork_env.validator import ValidationResult, ValidationIssue


def _lint(errors=0, warnings=0):
    issues = [LintIssue(line=i, level="error", message="e") for i in range(errors)]
    issues += [LintIssue(line=i, level="warning", message="w") for i in range(warnings)]
    return LintResult(issues=issues)


def _profile(total=10, empty=0):
    return ProfileResult(total=total, empty_count=empty, secret_count=3, safe_count=total - empty - 3)


def _val(errors=0, warnings=0):
    issues = [ValidationIssue(key=f"K{i}", level="error", message="e") for i in range(errors)]
    issues += [ValidationIssue(key=f"K{i}", level="warning", message="w") for i in range(warnings)]
    return ValidationResult(issues=issues)


def test_perfect_score():
    result = score_env(_lint(), _profile(), _val())
    assert result.total == 100
    assert result.grade() == "A"


def test_no_validation_gives_full_benefit():
    result = score_env(_lint(), _profile(), None)
    assert result.total == 100
    assert result.validation_score is None


def test_lint_errors_reduce_score():
    result = score_env(_lint(errors=3), _profile(), _val())
    assert result.lint_score == 40 - 24
    assert result.total < 100


def test_empty_values_reduce_profile_score():
    result = score_env(_lint(), _profile(total=10, empty=5), _val())
    assert result.profile_score == 15


def test_validation_errors_reduce_score():
    result = score_env(_lint(), _profile(), _val(errors=2))
    assert result.validation_score == 10


def test_grade_boundaries():
    def _score(n):
        r = ScoreResult(total=n, lint_score=0, profile_score=0, validation_score=0, summary="")
        return r.grade()
    assert _score(95) == "A"
    assert _score(80) == "B"
    assert _score(65) == "C"
    assert _score(45) == "D"
    assert _score(30) == "F"


def test_score_never_exceeds_100():
    result = score_env(_lint(), _profile(), _val())
    assert result.total <= 100


def test_score_never_below_zero():
    result = score_env(_lint(errors=20), _profile(total=10, empty=10), _val(errors=10))
    assert result.total >= 0
