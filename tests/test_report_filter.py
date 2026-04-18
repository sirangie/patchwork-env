import json
import pytest
from patchwork_env.filter import FilterResult
from patchwork_env.report_filter import render_filter_text, render_filter_json


@pytest.fixture
def result():
    return FilterResult(
        matched={"APP_NAME": "myapp", "DEBUG": "true"},
        excluded={"EMPTY_VAR": ""},
    )


def test_text_contains_header(result):
    out = render_filter_text(result)
    assert "Filter Results" in out


def test_text_shows_counts(result):
    out = render_filter_text(result)
    assert "Matched : 2" in out
    assert "Excluded: 1" in out


def test_text_lists_matched_keys(result):
    out = render_filter_text(result)
    assert "APP_NAME" in out
    assert "DEBUG" in out


def test_text_shows_values_when_requested(result):
    out = render_filter_text(result, show_values=True)
    assert "myapp" in out


def test_text_hides_values_by_default(result):
    out = render_filter_text(result)
    assert "myapp" not in out


def test_json_structure(result):
    data = json.loads(render_filter_json(result))
    assert "matched" in data
    assert "excluded" in data
    assert data["stats"]["matched"] == 2
    assert data["stats"]["excluded"] == 1


def test_json_matched_values(result):
    data = json.loads(render_filter_json(result))
    assert data["matched"]["APP_NAME"] == "myapp"
