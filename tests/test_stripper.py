"""tests for stripper.py"""
import pytest
from patchwork_env.stripper import strip_env


ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "secret",
    "DB_HOST": "localhost",
    "AWS_SECRET_KEY": "abc123",
    "PORT": "8080",
}


def test_no_filters_keeps_all():
    r = strip_env(ENV)
    assert r.stripped == ENV
    assert r.removed_count == 0


def test_explicit_key_removed():
    r = strip_env(ENV, keys=["PORT"])
    assert "PORT" not in r.stripped
    assert r.removed_count == 1


def test_explicit_reason_recorded():
    r = strip_env(ENV, keys=["APP_NAME"])
    assert r.ops[0].reason == "explicit"


def test_pattern_removes_matching_keys():
    r = strip_env(ENV, pattern=r"^DB_")
    assert "DB_PASSWORD" not in r.stripped
    assert "DB_HOST" not in r.stripped
    assert "APP_NAME" in r.stripped


def test_pattern_reason_recorded():
    r = strip_env(ENV, pattern=r"SECRET")
    for op in r.ops:
        assert op.reason == "pattern"


def test_combined_keys_and_pattern():
    r = strip_env(ENV, keys=["PORT"], pattern=r"^DB_")
    assert "PORT" not in r.stripped
    assert "DB_HOST" not in r.stripped
    assert "APP_NAME" in r.stripped


def test_missing_explicit_key_no_error():
    r = strip_env(ENV, keys=["NONEXISTENT"])
    assert r.removed_count == 0
    assert r.stripped == ENV


def test_original_unchanged():
    r = strip_env(ENV, keys=["PORT"])
    assert r.original == ENV
    assert "PORT" in r.original


def test_removed_keys_list():
    r = strip_env(ENV, keys=["PORT", "APP_NAME"])
    assert set(r.removed_keys) == {"PORT", "APP_NAME"}
