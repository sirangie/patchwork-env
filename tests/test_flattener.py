"""Tests for patchwork_env.flattener and patchwork_env.report_flattener."""
import json
import pytest
from patchwork_env.flattener import flatten_env, FlattenOp, FlattenResult
from patchwork_env.report_flattener import render_flatten_text, render_flatten_json


SAMPLE = {
    "DB__HOST": "localhost",
    "DB__PORT": "5432",
    "APP_NAME": "myapp",
    "aws__region": "us-east-1",
}


def test_double_underscore_replaced():
    result = flatten_env({"DB__HOST": "localhost"})
    assert "DB_HOST" in result.env


def test_original_key_removed():
    result = flatten_env({"DB__HOST": "localhost"})
    assert "DB__HOST" not in result.env


def test_value_preserved():
    result = flatten_env({"DB__HOST": "localhost"})
    assert result.env["DB_HOST"] == "localhost"


def test_unchanged_key_kept_as_is():
    result = flatten_env({"APP_NAME": "myapp"})
    assert "APP_NAME" in result.env
    assert result.env["APP_NAME"] == "myapp"


def test_uppercase_applied():
    result = flatten_env({"aws__region": "us-east-1"}, uppercase=True)
    assert "AWS_REGION" in result.env


def test_no_uppercase_preserves_case():
    result = flatten_env({"aws__region": "us-east-1"}, uppercase=False)
    assert "aws_region" in result.env


def test_changed_count():
    result = flatten_env(SAMPLE)
    assert result.changed_count == 3  # DB__HOST, DB__PORT, aws__region


def test_unchanged_count():
    result = flatten_env(SAMPLE)
    assert result.unchanged_count == 1  # APP_NAME


def test_renamed_keys_list():
    result = flatten_env({"DB__HOST": "x", "APP": "y"})
    assert "DB__HOST" in result.renamed_keys
    assert "APP" not in result.renamed_keys


def test_custom_separator_and_replacement():
    result = flatten_env({"DB.HOST": "localhost"}, separator=".", replacement="_", uppercase=False)
    assert "DB_HOST" in result.env


def test_render_text_contains_header():
    result = flatten_env(SAMPLE)
    text = render_flatten_text(result)
    assert "Flatten Report" in text


def test_render_text_shows_renamed_arrow():
    result = flatten_env({"DB__HOST": "x"})
    text = render_flatten_text(result)
    assert "->" in text


def test_render_text_shows_values_when_requested():
    result = flatten_env({"DB__HOST": "localhost"})
    text = render_flatten_text(result, show_values=True)
    assert "localhost" in text


def test_render_text_hides_values_by_default():
    result = flatten_env({"DB__HOST": "localhost"})
    text = render_flatten_text(result, show_values=False)
    assert "localhost" not in text


def test_render_json_structure():
    result = flatten_env(SAMPLE)
    data = json.loads(render_flatten_json(result))
    assert "total" in data
    assert "renamed_count" in data
    assert "ops" in data
    assert isinstance(data["ops"], list)


def test_render_json_op_fields():
    result = flatten_env({"DB__HOST": "localhost"})
    data = json.loads(render_flatten_json(result))
    op = data["ops"][0]
    assert op["original_key"] == "DB__HOST"
    assert op["flat_key"] == "DB_HOST"
    assert op["changed"] is True
