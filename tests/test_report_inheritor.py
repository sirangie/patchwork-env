"""Tests for patchwork_env.report_inheritor."""
import json
import pytest
from patchwork_env.inheritor import inherit_env
from patchwork_env.report_inheritor import render_inherit_text, render_inherit_json


PARENT = {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"}
CHILD = {"DB_HOST": "local-db", "APP_NAME": "myapp"}


@pytest.fixture
def result():
    return inherit_env(PARENT, CHILD)


def test_text_contains_header(result):
    text = render_inherit_text(result)
    assert "Inherit Report" in text


def test_text_shows_counts(result):
    text = render_inherit_text(result)
    assert "Inherited: 2" in text
    assert "Child-only: 2" in text
    assert "Overwritten: 0" in text


def test_text_marks_parent_keys(result):
    text = render_inherit_text(result)
    assert "(from parent)" in text


def test_text_marks_child_keys(result):
    text = render_inherit_text(result)
    assert "(child)" in text


def test_text_hides_values_by_default(result):
    text = render_inherit_text(result)
    assert "prod-db" not in text
    assert "local-db" not in text


def test_text_shows_values_when_requested(result):
    text = render_inherit_text(result, show_values=True)
    assert "local-db" in text


def test_text_overwrite_shows_overwritten_label():
    r = inherit_env(PARENT, CHILD, overwrite=True)
    text = render_inherit_text(r)
    assert "overwritten by parent" in text


def test_json_structure(result):
    data = json.loads(render_inherit_json(result))
    assert "inherited_count" in data
    assert "child_only_count" in data
    assert "overwritten_count" in data
    assert "ops" in data


def test_json_ops_have_required_fields(result):
    data = json.loads(render_inherit_json(result))
    for op in data["ops"]:
        assert "key" in op
        assert "source" in op
        assert "overwritten" in op


def test_json_counts_match(result):
    data = json.loads(render_inherit_json(result))
    assert data["inherited_count"] == result.inherited_count
    assert data["child_only_count"] == result.child_only_count
