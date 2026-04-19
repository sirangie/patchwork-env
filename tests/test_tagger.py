"""Tests for patchwork_env.tagger."""
import pytest
from patchwork_env.tagger import tag_env


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_ACCESS_KEY": "AKIA...",
    "AWS_SECRET": "secret",
    "APP_DEBUG": "true",
    "EMPTY": "",
}

RULES = {
    "database": ["DB_"],
    "aws": ["AWS_"],
    "app": ["APP_"],
}


def test_total_entries_matches_env():
    result = tag_env(ENV, RULES)
    assert len(result.entries) == len(ENV)


def test_database_tag_assigned():
    result = tag_env(ENV, RULES)
    assert set(result.keys_for("database")) == {"DB_HOST", "DB_PORT"}


def test_aws_tag_assigned():
    result = tag_env(ENV, RULES)
    assert set(result.keys_for("aws")) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_app_tag_assigned():
    result = tag_env(ENV, RULES)
    assert result.keys_for("app") == ["APP_DEBUG"]


def test_untagged_key_has_empty_tags():
    result = tag_env(ENV, RULES)
    assert result.tags_for("EMPTY") == []


def test_all_tags_sorted():
    result = tag_env(ENV, RULES)
    assert result.all_tags == sorted(result.all_tags)


def test_no_rules_no_tags():
    result = tag_env(ENV)
    assert result.all_tags == []
    for e in result.entries:
        assert e.tags == []


def test_key_can_have_multiple_tags():
    rules = {"infra": ["DB_", "AWS_"], "secrets": ["AWS_SECRET"]}
    result = tag_env(ENV, rules)
    tags = result.tags_for("AWS_SECRET")
    assert "infra" in tags
    assert "secrets" in tags


def test_tags_for_missing_key_returns_empty():
    result = tag_env(ENV, RULES)
    assert result.tags_for("NONEXISTENT") == []


def test_case_insensitive_pattern_match():
    result = tag_env({"db_host": "localhost"}, {"database": ["DB_"]})
    assert "db_host" in result.keys_for("database")
