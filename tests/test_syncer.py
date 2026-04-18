import pytest
from patchwork_env.differ import diff_envs
from patchwork_env.syncer import apply_diff, sync_summary


SOURCE = {"APP_ENV": "production", "DB_URL": "postgres://new", "NEW_KEY": "hello"}
TARGET = {"APP_ENV": "production", "DB_URL": "postgres://old", "OLD_KEY": "bye"}


def _diff():
    return diff_envs(SOURCE, TARGET)


def test_overwrite_changed():
    result = apply_diff(TARGET, _diff(), overwrite_changed=True, add_missing=False, remove_deleted=False)
    assert result["DB_URL"] == "postgres://new"
    assert result["OLD_KEY"] == "bye"  # untouched


def test_skip_overwrite_changed():
    result = apply_diff(TARGET, _diff(), overwrite_changed=False, add_missing=False, remove_deleted=False)
    assert result["DB_URL"] == "postgres://old"  # not overwritten


def test_add_missing():
    result = apply_diff(TARGET, _diff(), overwrite_changed=False, add_missing=True, remove_deleted=False)
    assert result["NEW_KEY"] == "hello"


def test_skip_add_missing():
    result = apply_diff(TARGET, _diff(), overwrite_changed=False, add_missing=False, remove_deleted=False)
    assert "NEW_KEY" not in result


def test_remove_deleted():
    result = apply_diff(TARGET, _diff(), overwrite_changed=False, add_missing=False, remove_deleted=True)
    assert "OLD_KEY" not in result


def test_skip_remove_deleted():
    result = apply_diff(TARGET, _diff(), overwrite_changed=False, add_missing=False, remove_deleted=False)
    assert "OLD_KEY" in result


def test_unchanged_keys_preserved():
    result = apply_diff(TARGET, _diff(), overwrite_changed=True, add_missing=True, remove_deleted=True)
    assert result["APP_ENV"] == "production"


def test_sync_summary_all_enabled():
    msg = sync_summary(_diff(), overwrite_changed=True, add_missing=True, remove_deleted=True)
    assert "updated" in msg
    assert "added" in msg
    assert "removed" in msg


def test_sync_summary_nothing():
    diff = diff_envs({"A": "1"}, {"A": "1"})
    msg = sync_summary(diff, overwrite_changed=True, add_missing=True, remove_deleted=True)
    assert msg == "Nothing to sync."
