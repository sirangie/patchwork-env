import pytest
from patchwork_env.profiler import profile_env, _is_likely_secret


def test_total_count():
    env = {"HOST": "localhost", "PORT": "5432", "DB_PASSWORD": "s3cr3t"}
    result = profile_env(env)
    assert result.total == 3


def test_empty_keys_detected():
    env = {"HOST": "localhost", "EMPTY_KEY": ""}
    result = profile_env(env)
    assert "EMPTY_KEY" in result.empty
    assert result.empty_count == 1


def test_secret_keys_detected():
    env = {"API_KEY": "abc", "DB_PASSWORD": "xyz", "HOST": "localhost"}
    result = profile_env(env)
    assert "API_KEY" in result.likely_secrets
    assert "DB_PASSWORD" in result.likely_secrets
    assert result.secret_count == 2


def test_safe_keys_detected():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = profile_env(env)
    assert "HOST" in result.safe
    assert "PORT" in result.safe
    assert result.safe_count == 2


def test_empty_not_counted_as_secret():
    env = {"API_KEY": ""}
    result = profile_env(env)
    assert "API_KEY" in result.empty
    assert "API_KEY" not in result.likely_secrets


def test_empty_env():
    result = profile_env({})
    assert result.total == 0
    assert result.empty == []
    assert result.likely_secrets == []
    assert result.safe == []


def test_is_likely_secret_various_hints():
    assert _is_likely_secret("DB_SECRET") is True
    assert _is_likely_secret("AUTH_TOKEN") is True
    assert _is_likely_secret("PRIVATE_KEY") is True
    assert _is_likely_secret("APP_HOST") is False
    assert _is_likely_secret("LOG_LEVEL") is False


def test_results_are_sorted():
    env = {"Z_TOKEN": "t", "A_TOKEN": "t", "HOST": "h"}
    result = profile_env(env)
    assert result.likely_secrets == sorted(result.likely_secrets)
    assert result.safe == sorted(result.safe)
