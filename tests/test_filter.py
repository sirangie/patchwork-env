import pytest
from patchwork_env.filter import filter_env, FilterResult


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
    "EMPTY_VAR": "",
    "APP_NAME": "myapp",
}


def test_no_filters_keeps_all():
    r = filter_env(SAMPLE)
    assert r.count == len(SAMPLE)
    assert r.excluded_count == 0


def test_pattern_filters_by_key():
    r = filter_env(SAMPLE, pattern="^APP_")
    assert "APP_NAME" in r.matched
    assert "DEBUG" not in r.matched


def test_exclude_empty_removes_blank_values():
    r = filter_env(SAMPLE, exclude_empty=True)
    assert "EMPTY_VAR" not in r.matched
    assert "EMPTY_VAR" in r.excluded


def test_keys_allowlist():
    r = filter_env(SAMPLE, keys=["DEBUG", "APP_NAME"])
    assert set(r.matched.keys()) == {"DEBUG", "APP_NAME"}


def test_invert_flips_match():
    r = filter_env(SAMPLE, pattern="^APP_", invert=True)
    assert "APP_NAME" not in r.matched
    assert "APP_NAME" in r.excluded
    assert "DEBUG" in r.matched


def test_combined_pattern_and_exclude_empty():
    env = {"APP_URL": "http://x", "APP_TOKEN": "", "OTHER": "val"}
    r = filter_env(env, pattern="^APP_", exclude_empty=True)
    assert "APP_URL" in r.matched
    assert "APP_TOKEN" not in r.matched
    assert "OTHER" not in r.matched


def test_count_properties():
    r = filter_env(SAMPLE, pattern="SECRET")
    assert r.count == len(r.matched)
    assert r.excluded_count == len(r.excluded)
    assert r.count + r.excluded_count == len(SAMPLE)
