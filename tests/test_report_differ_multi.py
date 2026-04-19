import json
import pytest
from patchwork_env.differ_multi import diff_multi
from patchwork_env.report_differ_multi import render_multi_text, render_multi_json

BASE = {"A": "1", "B": "2", "C": "3"}
DEV = {"A": "1", "B": "99", "D": "4"}
PROD = {"A": "1", "B": "2", "C": "3"}


@pytest.fixture
def result():
    return diff_multi(BASE, {"dev": DEV, "prod": PROD}, base_label="local")


def test_text_contains_base_label(result):
    text = render_multi_text(result)
    assert "local" in text


def test_text_contains_env_labels(result):
    text = render_multi_text(result)
    assert "[dev]" in text
    assert "[prod]" in text


def test_text_shows_no_differences_for_identical(result):
    text = render_multi_text(result)
    assert "no differences" in text


def test_text_shows_changed_key(result):
    text = render_multi_text(result)
    assert "B" in text


def test_text_summary_present(result):
    text = render_multi_text(result)
    assert "Summary" in text


def test_json_has_diffs_key(result):
    data = json.loads(render_multi_json(result))
    assert "diffs" in data


def test_json_base_field(result):
    data = json.loads(render_multi_json(result))
    assert data["base"] == "local"


def test_json_summary_field(result):
    data = json.loads(render_multi_json(result))
    assert "summary" in data
    assert "dev" in data["summary"]


def test_json_entries_have_status(result):
    data = json.loads(render_multi_json(result))
    for entry in data["diffs"]["dev"]:
        assert "status" in entry
        assert "key" in entry
