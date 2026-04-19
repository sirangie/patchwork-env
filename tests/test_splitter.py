import pytest
from patchwork_env.splitter import split_env, SplitResult


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "mydb",
    "AWS_KEY": "AKIA123",
    "AWS_SECRET": "secret",
    "APP_ENV": "production",
    "APP_DEBUG": "false",
    "STANDALONE": "yes",
}


def test_inferred_prefixes_split_correctly():
    result = split_env(SAMPLE)
    assert "DB" in result.bucket_names
    assert "AWS" in result.bucket_names
    assert "APP" in result.bucket_names


def test_unmatched_contains_standalone():
    result = split_env(SAMPLE)
    assert "STANDALONE" in result.unmatched


def test_keys_in_db_bucket():
    result = split_env(SAMPLE)
    assert set(result.keys_in("DB")) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_total_keys_matches_input():
    result = split_env(SAMPLE)
    assert result.total_keys == len(SAMPLE)


def test_explicit_prefixes_override_infer():
    result = split_env(SAMPLE, prefixes=["DB"])
    assert "AWS" not in result.bucket_names
    assert "DB" in result.bucket_names
    assert "AWS_KEY" in result.unmatched


def test_infer_false_no_prefixes():
    result = split_env(SAMPLE, infer=False)
    assert result.buckets == {}
    assert set(result.unmatched.keys()) == set(SAMPLE.keys())


def test_empty_env_returns_empty_result():
    result = split_env({})
    assert result.total_keys == 0
    assert result.buckets == {}
    assert result.unmatched == {}


def test_single_prefix_key_not_inferred():
    env = {"DB_HOST": "localhost", "SOLO": "1"}
    result = split_env(env)
    # DB only has one key, so not inferred as a prefix group
    assert "DB" not in result.bucket_names
    assert "DB_HOST" in result.unmatched


def test_bucket_names_property():
    result = split_env(SAMPLE)
    assert isinstance(result.bucket_names, list)
    assert len(result.bucket_names) >= 1


def test_values_preserved_in_bucket():
    result = split_env(SAMPLE)
    assert result.buckets["DB"]["DB_HOST"] == "localhost"
