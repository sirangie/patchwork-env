"""Tests for report_differ_schema rendering."""
import json
import pytest
from patchwork_env.differ_schema import SchemaField, diff_schema
from patchwork_env.report_differ_schema import render_schema_diff_text, render_schema_diff_json


@pytest.fixture()
def clean_result():
    env = {"HOST": "localhost", "PORT": "5432"}
    schema = [
        SchemaField("HOST", required=True, description="DB host"),
        SchemaField("PORT", required=True),
    ]
    return diff_schema(env, schema, env_label="staging", schema_label="spec")


@pytest.fixture()
def dirty_result():
    env = {"HOST": "localhost"}
    schema = [
        SchemaField("HOST", required=True),
        SchemaField("PORT", required=True, default="5432"),
        SchemaField("DEBUG", required=False),
    ]
    return diff_schema(env, schema, allow_extra=False)


def test_text_contains_header(clean_result):
    text = render_schema_diff_text(clean_result)
    assert "Schema Diff" in text
    assert "staging" in text


def test_text_ok_status(clean_result):
    text = render_schema_diff_text(clean_result)
    assert "OK" in text


def test_text_fail_status(dirty_result):
    text = render_schema_diff_text(dirty_result)
    assert "FAIL" in text


def test_text_shows_description(clean_result):
    text = render_schema_diff_text(clean_result, show_descriptions=True)
    assert "DB host" in text


def test_text_hides_description_when_disabled(clean_result):
    text = render_schema_diff_text(clean_result, show_descriptions=False)
    assert "DB host" not in text


def test_text_shows_default_for_missing(dirty_result):
    text = render_schema_diff_text(dirty_result)
    assert "5432" in text


def test_json_ok_field(clean_result):
    data = json.loads(render_schema_diff_json(clean_result))
    assert data["ok"] is True


def test_json_summary_counts(dirty_result):
    data = json.loads(render_schema_diff_json(dirty_result))
    assert data["summary"]["missing_required"] == 1
    assert data["summary"]["missing_optional"] == 1


def test_json_entries_present(clean_result):
    data = json.loads(render_schema_diff_json(clean_result))
    keys = [e["key"] for e in data["entries"]]
    assert "HOST" in keys
    assert "PORT" in keys


def test_json_labels_stored(clean_result):
    data = json.loads(render_schema_diff_json(clean_result))
    assert data["env_label"] == "staging"
    assert data["schema_label"] == "spec"
