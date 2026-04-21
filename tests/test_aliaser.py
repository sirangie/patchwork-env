"""Tests for patchwork_env.aliaser and patchwork_env.report_aliaser."""
import json
import pytest
from patchwork_env.aliaser import alias_env, AliasOp, AliasResult
from patchwork_env.report_aliaser import render_alias_text, render_alias_json


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PASS": "secret",
    "APP_PORT": "8080",
}


def test_alias_renames_key():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_original_removed_by_default():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" not in result.env


def test_keep_original_retains_both_keys():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"}, keep_original=True)
    assert "DB_HOST" in result.env
    assert "DATABASE_HOST" in result.env


def test_missing_key_is_skipped():
    result = alias_env(SAMPLE_ENV, {"MISSING_KEY": "NEW_KEY"})
    assert result.skipped_count == 1
    op = result.ops[0]
    assert op.skipped
    assert op.reason == "key not found"


def test_existing_alias_skipped_without_overwrite():
    env = {**SAMPLE_ENV, "DATABASE_HOST": "other"}
    result = alias_env(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=False)
    assert result.skipped_count == 1
    assert result.env["DATABASE_HOST"] == "other"  # unchanged


def test_existing_alias_overwritten_when_flag_set():
    env = {**SAMPLE_ENV, "DATABASE_HOST": "other"}
    result = alias_env(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=True)
    assert result.aliased_count == 1
    assert result.env["DATABASE_HOST"] == "localhost"


def test_aliased_count_accurate():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "H", "DB_PASS": "P", "NOPE": "X"})
    assert result.aliased_count == 2
    assert result.skipped_count == 1


def test_aliased_keys_list():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "H", "DB_PASS": "P"})
    assert set(result.aliased_keys) == {"H", "P"}


def test_unrelated_keys_preserved():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "APP_PORT" in result.env
    assert result.env["APP_PORT"] == "8080"


# --- report tests ---

def test_render_text_contains_header():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    text = render_alias_text(result)
    assert "Alias Report" in text


def test_render_text_shows_counts():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "H", "NOPE": "X"})
    text = render_alias_text(result)
    assert "Aliased : 1" in text
    assert "Skipped : 1" in text


def test_render_text_shows_arrow_for_aliased():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    text = render_alias_text(result)
    assert "->" in text and "DB_HOST" in text


def test_render_text_shows_skip_reason():
    result = alias_env(SAMPLE_ENV, {"MISSING": "X"})
    text = render_alias_text(result)
    assert "SKIP" in text
    assert "key not found" in text


def test_render_json_structure():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    data = json.loads(render_alias_json(result))
    assert "aliased_count" in data
    assert "skipped_count" in data
    assert "aliased_keys" in data
    assert isinstance(data["ops"], list)


def test_render_json_op_fields():
    result = alias_env(SAMPLE_ENV, {"DB_HOST": "DATABASE_HOST"})
    data = json.loads(render_alias_json(result))
    op = data["ops"][0]
    assert op["original_key"] == "DB_HOST"
    assert op["alias_key"] == "DATABASE_HOST"
    assert op["skipped"] is False
