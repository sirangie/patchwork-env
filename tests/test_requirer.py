"""Tests for patchwork_env.requirer."""
import pytest
from patchwork_env.requirer import require_env, RequireOp, RequireResult


SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
    "EXTRA_KEY": "surprise",
}


def test_all_required_present_is_ok():
    result = require_env(SAMPLE_ENV, required=["DATABASE_URL", "SECRET_KEY"])
    assert result.ok is True


def test_missing_required_key_not_ok():
    result = require_env(SAMPLE_ENV, required=["DATABASE_URL", "MISSING_KEY"])
    assert result.ok is False


def test_missing_required_in_list():
    result = require_env(SAMPLE_ENV, required=["DATABASE_URL", "MISSING_KEY"])
    missing = [o.key for o in result.missing_required]
    assert "MISSING_KEY" in missing
    assert "DATABASE_URL" not in missing


def test_present_keys_have_values():
    result = require_env(SAMPLE_ENV, required=["DATABASE_URL", "SECRET_KEY"])
    present = {o.key: o.value for o in result.present_keys}
    assert present["DATABASE_URL"] == "postgres://localhost/db"
    assert present["SECRET_KEY"] == "abc123"


def test_optional_missing_does_not_fail():
    result = require_env(
        SAMPLE_ENV,
        required=["DATABASE_URL"],
        optional=["OPTIONAL_KEY"],
    )
    assert result.ok is True
    missing_opt = [o.key for o in result.missing_optional]
    assert "OPTIONAL_KEY" in missing_opt


def test_extra_keys_detected():
    result = require_env(
        SAMPLE_ENV,
        required=["DATABASE_URL"],
        optional=["SECRET_KEY", "DEBUG"],
    )
    extra = [o.key for o in result.extra_keys]
    assert "EXTRA_KEY" in extra


def test_extras_allowed_by_default_does_not_fail():
    result = require_env(
        SAMPLE_ENV,
        required=["DATABASE_URL"],
        allow_extras=True,
    )
    assert result.ok is True


def test_extras_disallowed_fails():
    result = require_env(
        SAMPLE_ENV,
        required=["DATABASE_URL"],
        optional=["SECRET_KEY", "DEBUG"],
        allow_extras=False,
    )
    assert result.ok is False
    assert len(result.extra_keys) > 0


def test_empty_env_all_required_missing():
    result = require_env({}, required=["FOO", "BAR"])
    assert result.ok is False
    assert len(result.missing_required) == 2


def test_repr_op():
    op = RequireOp(key="FOO", status="missing", required=True)
    assert "FOO" in repr(op)
    assert "required" in repr(op)
