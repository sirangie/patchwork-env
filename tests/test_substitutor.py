"""Tests for substitutor.py and report_substitutor.py."""
import json

import pytest

from patchwork_env.substitutor import substitute_env, SubstituteOp, SubstituteResult
from patchwork_env.report_substitutor import render_substitute_text, render_substitute_json


SAMPLE_ENV = {
    "DB_HOST": "PLACEHOLDER",
    "DB_PORT": "5432",
    "API_KEY": "PLACEHOLDER",
    "APP_NAME": "myapp",
}


def test_substituted_key_gets_new_value():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "prod-db.example.com"})
    assert result.env["DB_HOST"] == "prod-db.example.com"


def test_unrelated_keys_unchanged():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "prod-db.example.com"})
    assert result.env["DB_PORT"] == "5432"
    assert result.env["APP_NAME"] == "myapp"


def test_substituted_count_correct():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h1", "API_KEY": "secret"})
    assert result.substituted_count == 2


def test_unchanged_count_correct():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h1"})
    assert result.unchanged_count == 3


def test_substituted_keys_listed():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h1", "API_KEY": "k"})
    assert "DB_HOST" in result.substituted_keys
    assert "API_KEY" in result.substituted_keys


def test_missing_key_in_mapping_ignored():
    result = substitute_env(SAMPLE_ENV, {"NONEXISTENT": "value"})
    assert result.substituted_count == 0


def test_same_value_not_recorded_as_op():
    result = substitute_env(SAMPLE_ENV, {"DB_PORT": "5432"})
    assert result.substituted_count == 0


def test_only_placeholders_skips_non_placeholder():
    result = substitute_env(
        SAMPLE_ENV,
        {"DB_HOST": "real-host", "DB_PORT": "9999"},
        placeholder="PLACEHOLDER",
        only_placeholders=True,
    )
    assert result.env["DB_HOST"] == "real-host"
    assert result.env["DB_PORT"] == "5432"  # not a placeholder, should be skipped


def test_only_placeholders_substitutes_matching():
    result = substitute_env(
        SAMPLE_ENV,
        {"API_KEY": "new-secret"},
        placeholder="PLACEHOLDER",
        only_placeholders=True,
    )
    assert result.env["API_KEY"] == "new-secret"
    assert result.substituted_count == 1


def test_op_records_old_and_new_value():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "newhost"})
    op = result.ops[0]
    assert op.old_value == "PLACEHOLDER"
    assert op.new_value == "newhost"
    assert op.key == "DB_HOST"


# --- report tests ---

def test_render_text_contains_header():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h"})
    text = render_substitute_text(result)
    assert "Substitutor" in text


def test_render_text_shows_substituted_key():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h"})
    text = render_substitute_text(result)
    assert "DB_HOST" in text


def test_render_text_no_ops_message():
    result = substitute_env(SAMPLE_ENV, {})
    text = render_substitute_text(result)
    assert "no substitutions" in text


def test_render_text_show_values():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "prod"})
    text = render_substitute_text(result, show_values=True)
    assert "prod" in text
    assert "PLACEHOLDER" in text


def test_render_json_structure():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "h", "API_KEY": "k"})
    data = json.loads(render_substitute_json(result))
    assert data["substituted_count"] == 2
    assert "substitutions" in data
    assert isinstance(data["substitutions"], list)


def test_render_json_substitution_fields():
    result = substitute_env(SAMPLE_ENV, {"DB_HOST": "newhost"})
    data = json.loads(render_substitute_json(result))
    sub = data["substitutions"][0]
    assert sub["key"] == "DB_HOST"
    assert sub["old_value"] == "PLACEHOLDER"
    assert sub["new_value"] == "newhost"
