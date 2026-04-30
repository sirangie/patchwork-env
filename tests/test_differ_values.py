"""Tests for patchwork_env.differ_values."""
import pytest
from patchwork_env.differ_values import diff_values, ValueDiffEntry, ValueDiffResult


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
STAGING = {"DB_HOST": "staging.db", "DB_PORT": "5432", "SECRET": "xyz"}
PROD = {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET": "supersecret", "EXTRA": "yes"}


@pytest.fixture
def result() -> ValueDiffResult:
    return diff_values(BASE, "local", [STAGING, PROD], ["staging", "prod"])


def test_all_labels_present(result):
    assert result.all_labels == ["local", "staging", "prod"]


def test_base_label_stored(result):
    assert result.base_label == "local"


def test_target_labels_stored(result):
    assert result.target_labels == ["staging", "prod"]


def test_entries_cover_all_keys(result):
    keys = {e.key for e in result.entries}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "SECRET" in keys
    assert "EXTRA" in keys


def test_consistent_key_detected(result):
    entry = result.for_key("DB_PORT")
    assert entry is not None
    assert entry.is_consistent


def test_inconsistent_key_detected(result):
    entry = result.for_key("DB_HOST")
    assert entry is not None
    assert not entry.is_consistent


def test_has_differences_true(result):
    assert result.has_differences


def test_inconsistent_list_contains_db_host(result):
    keys = {e.key for e in result.inconsistent}
    assert "DB_HOST" in keys


def test_consistent_list_contains_db_port(result):
    keys = {e.key for e in result.consistent}
    assert "DB_PORT" in keys


def test_missing_in_base_shows_none(result):
    entry = result.for_key("EXTRA")
    assert entry is not None
    assert "local" in entry.missing_in


def test_missing_in_returns_empty_when_present_everywhere():
    r = diff_values({"K": "v"}, "a", [{"K": "v"}], ["b"])
    entry = r.for_key("K")
    assert entry.missing_in == []


def test_identical_envs_no_differences():
    env = {"FOO": "bar", "BAZ": "qux"}
    r = diff_values(env, "base", [dict(env)], ["copy"])
    assert not r.has_differences


def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        diff_values(BASE, "base", [STAGING, PROD], ["staging"])


def test_for_key_missing_returns_none(result):
    assert result.for_key("NONEXISTENT") is None
