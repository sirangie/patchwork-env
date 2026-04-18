import pytest
from patchwork_env.validator import validate_env, ValidationIssue


TEMPLATE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "changeme",
    "OPTIONAL_FLAG": "",
}


def test_all_present_no_issues():
    env = {"DATABASE_URL": "postgres://prod/db", "SECRET_KEY": "abc123", "OPTIONAL_FLAG": "true"}
    result = validate_env(env, TEMPLATE)
    assert result.ok
    assert result.issues == []


def test_missing_required_key_is_error():
    env = {"SECRET_KEY": "abc123"}
    result = validate_env(env, TEMPLATE)
    assert not result.ok
    errors = [i.key for i in result.errors]
    assert "DATABASE_URL" in errors


def test_missing_optional_key_is_warning():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y"}
    result = validate_env(env, TEMPLATE)
    assert result.ok  # no errors
    warnings = [i.key for i in result.warnings]
    assert "OPTIONAL_FLAG" in warnings


def test_empty_value_is_warning():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "", "OPTIONAL_FLAG": ""}
    result = validate_env(env, TEMPLATE)
    assert result.ok
    warn_keys = [i.key for i in result.warnings]
    assert "SECRET_KEY" in warn_keys


def test_extra_keys_allowed_by_default():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "EXTRA": "z"}
    result = validate_env(env, TEMPLATE)
    assert result.ok
    assert all(i.key != "EXTRA" for i in result.issues)


def test_extra_keys_flagged_when_disallowed():
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "EXTRA": "z"}
    result = validate_env(env, TEMPLATE, allow_extra=False)
    warn_keys = [i.key for i in result.warnings]
    assert "EXTRA" in warn_keys


def test_validation_issue_repr():
    issue = ValidationIssue("FOO", "error", "required key is missing")
    assert "ERROR" in repr(issue)
    assert "FOO" in repr(issue)
