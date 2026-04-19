import pytest
from patchwork_env.grouper import group_env


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "mydb",
    "AWS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "APP_NAME": "patchwork",
    "APP_ENV": "production",
    "STANDALONE": "yes",
}


def test_inferred_prefixes_grouped():
    result = group_env(ENV)
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert "APP" in result.groups


def test_ungrouped_contains_standalone():
    result = group_env(ENV)
    assert "STANDALONE" in result.ungrouped


def test_group_keys_correct():
    result = group_env(ENV)
    assert set(result.keys_in("DB")) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_total_keys_matches():
    result = group_env(ENV)
    assert result.total_keys == len(ENV)


def test_explicit_prefixes():
    result = group_env(ENV, prefixes=["DB"])
    assert "DB" in result.groups
    assert "AWS" not in result.groups
    assert "AWS_KEY" in result.ungrouped


def test_no_separator_keys_are_ungrouped():
    env = {"PLAIN": "1", "ALSO": "2"}
    result = group_env(env)
    assert result.ungrouped == env
    assert result.groups == {}


def test_prefix_appearing_once_not_inferred():
    env = {"DB_HOST": "h", "LONELY_KEY": "v", "OTHER": "x"}
    result = group_env(env)
    # DB only appears once so should NOT be grouped automatically
    assert "DB" not in result.groups
    assert "DB_HOST" in result.ungrouped


def test_group_names_sorted():
    result = group_env(ENV)
    assert result.group_names == sorted(result.group_names)
