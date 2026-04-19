import pytest
from patchwork_env.scoper import scope_env


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_included_keys_match_prefix():
    result = scope_env(ENV, "DB")
    assert set(result.included) == {"DB_HOST", "DB_PORT"}


def test_excluded_keys_are_rest():
    result = scope_env(ENV, "DB")
    assert "APP_NAME" in result.excluded
    assert "SECRET_KEY" in result.excluded


def test_env_contains_only_scoped_keys():
    result = scope_env(ENV, "APP")
    assert set(result.env.keys()) == {"APP_NAME", "APP_DEBUG"}


def test_env_values_preserved():
    result = scope_env(ENV, "DB")
    assert result.env["DB_HOST"] == "localhost"
    assert result.env["DB_PORT"] == "5432"


def test_strip_prefix_removes_scope():
    result = scope_env(ENV, "DB", strip_prefix=True)
    assert "HOST" in result.env
    assert "PORT" in result.env
    assert "DB_HOST" not in result.env


def test_strip_prefix_values_unchanged():
    result = scope_env(ENV, "DB", strip_prefix=True)
    assert result.env["HOST"] == "localhost"


def test_counts_match():
    result = scope_env(ENV, "APP")
    assert result.included_count == 2
    assert result.excluded_count == 3
    assert result.total == 5


def test_unknown_scope_returns_empty_env():
    result = scope_env(ENV, "REDIS")
    assert result.env == {}
    assert result.included == []
    assert result.excluded_count == len(ENV)


def test_scope_label_stored():
    result = scope_env(ENV, "DB")
    assert result.scope == "DB"


def test_case_insensitive_default():
    env = {"db_host": "h", "APP_NAME": "n"}
    result = scope_env(env, "DB")
    assert "db_host" in result.included
