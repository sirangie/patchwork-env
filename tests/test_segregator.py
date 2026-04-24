"""Tests for patchwork_env.segregator."""
import pytest
from patchwork_env.segregator import segregate_env, SegregateResult


@pytest.fixture()
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_xyz",
        "LOG_LEVEL": "info",
    }


def test_total_keys_matches_input(sample_env):
    result = segregate_env(sample_env)
    assert result.total == len(sample_env)


def test_public_keys_are_non_secret(sample_env):
    result = segregate_env(sample_env)
    assert "APP_NAME" in result.public
    assert "DEBUG" in result.public
    assert "PORT" in result.public
    assert "LOG_LEVEL" in result.public


def test_private_keys_are_secret(sample_env):
    result = segregate_env(sample_env)
    assert "DATABASE_PASSWORD" in result.private
    assert "API_KEY" in result.private
    assert "AUTH_TOKEN" in result.private


def test_no_overlap_between_buckets(sample_env):
    result = segregate_env(sample_env)
    overlap = set(result.public) & set(result.private)
    assert overlap == set()


def test_counts_sum_to_total(sample_env):
    result = segregate_env(sample_env)
    assert result.public_count + result.private_count == result.total


def test_keys_in_public_bucket(sample_env):
    result = segregate_env(sample_env)
    assert result.keys_in("public") == sorted(result.public)


def test_keys_in_private_bucket(sample_env):
    result = segregate_env(sample_env)
    assert result.keys_in("private") == sorted(result.private)


def test_keys_in_unknown_bucket_returns_empty(sample_env):
    result = segregate_env(sample_env)
    assert result.keys_in("other") == []


def test_extra_private_pattern():
    env = {"INTERNAL_URL": "http://localhost", "PORT": "3000"}
    result = segregate_env(env, extra_private_patterns=[r"internal"])
    assert "INTERNAL_URL" in result.private
    assert "PORT" in result.public


def test_empty_env_gives_empty_result():
    result = segregate_env({})
    assert result.total == 0
    assert result.public_count == 0
    assert result.private_count == 0


def test_all_public_env():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
    result = segregate_env(env)
    assert result.private_count == 0
    assert result.public_count == 3


def test_all_private_env():
    env = {"DB_PASSWORD": "x", "API_KEY": "y", "SECRET": "z"}
    result = segregate_env(env)
    assert result.public_count == 0
    assert result.private_count == 3
