"""Tests for patchwork_env.cloner."""
import pytest
from patchwork_env.cloner import clone_env, CloneResult


ENV = {
    "DEV_HOST": "localhost",
    "DEV_PORT": "5432",
    "DEV_SECRET": "s3cr3t",
    "PROD_HOST": "prod.example.com",
    "UNRELATED": "value",
}


def test_cloned_keys_present():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert "STAGING_HOST" in result.env
    assert "STAGING_PORT" in result.env
    assert "STAGING_SECRET" in result.env


def test_non_matching_keys_preserved():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert result.env["UNRELATED"] == "value"
    assert result.env["PROD_HOST"] == "prod.example.com"


def test_values_copied_correctly():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert result.env["STAGING_HOST"] == "localhost"
    assert result.env["STAGING_PORT"] == "5432"


def test_cloned_count():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert result.cloned_count == 3


def test_skipped_count_zero_when_no_conflicts():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert result.skipped_count == 0


def test_skip_existing_without_overwrite():
    result = clone_env(ENV, "DEV_", "PROD_")
    # PROD_HOST already exists; should be skipped
    skipped = [o for o in result.ops if o.skipped]
    assert any(o.cloned_key == "PROD_HOST" for o in skipped)


def test_overwrite_replaces_existing():
    result = clone_env(ENV, "DEV_", "PROD_", overwrite=True)
    assert result.env["PROD_HOST"] == "localhost"


def test_cloned_keys_list():
    result = clone_env(ENV, "DEV_", "STAGING_")
    assert set(result.cloned_keys) == {"STAGING_HOST", "STAGING_PORT", "STAGING_SECRET"}


def test_no_prefix_match_returns_unchanged():
    result = clone_env(ENV, "MISSING_", "NEW_")
    assert result.cloned_count == 0
    assert result.env == ENV


def test_strip_prefix_false_prepends_full_key():
    result = clone_env({"DEV_HOST": "localhost"}, "DEV_", "COPY_", strip_source_prefix=False)
    assert "COPY_DEV_HOST" in result.env
    assert "COPY_HOST" not in result.env


def test_skipped_reason_is_exists():
    result = clone_env(ENV, "DEV_", "PROD_")
    for op in result.ops:
        if op.skipped:
            assert op.reason == "exists"
