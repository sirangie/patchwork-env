import pytest
from patchwork_env.promoter import promote_env, PromoteResult


SOURCE = {"DB_URL": "postgres://prod", "API_KEY": "secret", "EMPTY_VAL": "", "DEBUG": "false"}
TARGET = {"DB_URL": "postgres://staging", "APP_NAME": "myapp"}


def test_basic_promote_adds_missing_key():
    result = promote_env(SOURCE, TARGET, keys=["API_KEY"])
    assert "API_KEY" in result.env
    assert result.env["API_KEY"] == "secret"


def test_existing_key_skipped_without_overwrite():
    result = promote_env(SOURCE, TARGET, keys=["DB_URL"])
    assert result.env["DB_URL"] == "postgres://staging"
    assert result.skipped_count == 1


def test_overwrite_replaces_existing_key():
    result = promote_env(SOURCE, TARGET, keys=["DB_URL"], overwrite=True)
    assert result.env["DB_URL"] == "postgres://prod"
    assert result.promoted_count == 1


def test_empty_value_skipped_by_default():
    result = promote_env(SOURCE, TARGET, keys=["EMPTY_VAL"])
    assert result.skipped_count == 1
    op = result.ops[0]
    assert op.reason == "empty value"


def test_empty_value_allowed_when_guard_off():
    result = promote_env(SOURCE, TARGET, keys=["EMPTY_VAL"], guard_empty=False)
    assert result.promoted_count == 1
    assert result.env["EMPTY_VAL"] == ""


def test_blocked_key_not_promoted():
    result = promote_env(SOURCE, TARGET, keys=["API_KEY"], blocked_keys=["API_KEY"])
    assert result.blocked_count == 1
    assert "API_KEY" not in result.env


def test_missing_source_key_is_skipped():
    result = promote_env(SOURCE, TARGET, keys=["NONEXISTENT"])
    assert result.skipped_count == 1
    assert result.ops[0].reason == "not in source"


def test_target_unchanged_keys_preserved():
    result = promote_env(SOURCE, TARGET, keys=["DEBUG"])
    assert result.env["APP_NAME"] == "myapp"


def test_promoted_keys_list():
    result = promote_env(SOURCE, TARGET, keys=["API_KEY", "DEBUG"])
    assert set(result.promoted_keys) == {"API_KEY", "DEBUG"}


def test_all_source_keys_when_no_filter():
    small_src = {"X": "1", "Y": "2"}
    result = promote_env(small_src, {})
    assert result.promoted_count == 2
    assert result.env == {"X": "1", "Y": "2"}


def test_repr_op():
    result = promote_env(SOURCE, TARGET, keys=["API_KEY"])
    op = result.ops[0]
    assert "promoted" in repr(op)
    assert "API_KEY" in repr(op)
