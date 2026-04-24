"""Tests for patchwork_env.defaulter."""
import pytest
from patchwork_env.defaulter import apply_defaults, DefaultOp, DefaultResult


DEFAULTS = {
    "LOG_LEVEL": "info",
    "TIMEOUT": "30",
    "DEBUG": "false",
}


def test_missing_key_is_filled():
    result = apply_defaults({}, {"LOG_LEVEL": "info"})
    assert result.env["LOG_LEVEL"] == "info"


def test_present_key_not_overwritten():
    result = apply_defaults({"LOG_LEVEL": "debug"}, {"LOG_LEVEL": "info"})
    assert result.env["LOG_LEVEL"] == "debug"


def test_applied_count_correct():
    env = {"LOG_LEVEL": "debug"}
    result = apply_defaults(env, DEFAULTS)
    assert result.applied_count == 2  # TIMEOUT and DEBUG are missing


def test_skipped_count_correct():
    env = {"LOG_LEVEL": "debug"}
    result = apply_defaults(env, DEFAULTS)
    assert result.skipped_count == 1  # LOG_LEVEL is present


def test_applied_keys_listed():
    result = apply_defaults({}, DEFAULTS)
    assert set(result.applied_keys) == {"LOG_LEVEL", "TIMEOUT", "DEBUG"}


def test_original_env_not_mutated():
    original = {"A": "1"}
    apply_defaults(original, {"B": "2"})
    assert "B" not in original


def test_overwrite_empty_false_keeps_empty_value():
    result = apply_defaults({"TIMEOUT": ""}, {"TIMEOUT": "30"}, overwrite_empty=False)
    assert result.env["TIMEOUT"] == ""
    assert result.applied_count == 0


def test_overwrite_empty_true_fills_empty_value():
    result = apply_defaults({"TIMEOUT": ""}, {"TIMEOUT": "30"}, overwrite_empty=True)
    assert result.env["TIMEOUT"] == "30"
    assert result.applied_count == 1


def test_reason_missing_recorded():
    result = apply_defaults({}, {"LOG_LEVEL": "info"})
    op = result.ops[0]
    assert op.reason == "missing"
    assert op.applied is True


def test_reason_present_recorded():
    result = apply_defaults({"LOG_LEVEL": "debug"}, {"LOG_LEVEL": "info"})
    op = result.ops[0]
    assert op.reason == "present"
    assert op.applied is False


def test_reason_empty_recorded_when_overwrite():
    result = apply_defaults({"TIMEOUT": ""}, {"TIMEOUT": "30"}, overwrite_empty=True)
    op = result.ops[0]
    assert op.reason == "empty"


def test_empty_defaults_leaves_env_unchanged():
    env = {"A": "1", "B": "2"}
    result = apply_defaults(env, {})
    assert result.env == env
    assert result.applied_count == 0


def test_all_keys_present_in_result_env():
    env = {"EXISTING": "yes"}
    defaults = {"NEW_KEY": "new_val"}
    result = apply_defaults(env, defaults)
    assert "EXISTING" in result.env
    assert "NEW_KEY" in result.env
