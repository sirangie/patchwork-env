import json
import pytest
from patchwork_env.comparator import compare_envs
from patchwork_env.report_comparator import render_compare_text, render_compare_json


L = {"A": "1", "B": "old", "C": "only-left"}
R = {"A": "1", "B": "new", "D": "only-right"}


@pytest.fixture
def result():
    return compare_envs(L, R, left_label="dev", right_label="prod")


def test_text_contains_labels(result):
    out = render_compare_text(result)
    assert "dev" in out and "prod" in out


def test_text_shows_added(result):
    out = render_compare_text(result)
    assert "+ D" in out


def test_text_shows_removed(result):
    out = render_compare_text(result)
    assert "- C" in out


def test_text_shows_changed(result):
    out = render_compare_text(result)
    assert "~ B" in out


def test_text_identical_message():
    r = compare_envs({"X": "1"}, {"X": "1"})
    out = render_compare_text(r)
    assert "identical" in out.lower()


def test_json_structure(result):
    out = render_compare_json(result)
    data = json.loads(out)
    assert "summary" in data
    assert "entries" in data
    assert data["identical"] is False


def test_json_summary_counts(result):
    data = json.loads(render_compare_json(result))
    assert data["summary"]["added"] == 1
    assert data["summary"]["removed"] == 1
    assert data["summary"]["changed"] == 1
    assert data["summary"]["same"] == 1


def test_json_identical_flag():
    r = compare_envs({"K": "v"}, {"K": "v"})
    data = json.loads(render_compare_json(r))
    assert data["identical"] is True
