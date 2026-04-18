import json
import pytest
from patchwork_env.renamer import rename_keys
from patchwork_env.report_renamer import render_rename_text, render_rename_json


ENV = {"OLD": "val", "KEEP": "other", "TARGET": "exists"}


@pytest.fixture
def result():
    return rename_keys(ENV, {"OLD": "RENAMED", "MISSING": "X", "KEEP": "TARGET"})


def test_text_contains_header(result):
    out = render_rename_text(result)
    assert "Rename Report" in out


def test_text_shows_renamed(result):
    out = render_rename_text(result)
    assert "RENAMED" in out


def test_text_shows_skipped(result):
    out = render_rename_text(result)
    assert "MISSING" in out


def test_text_shows_conflict(result):
    out = render_rename_text(result)
    assert "TARGET" in out
    assert "Conflict" in out or "conflict" in out


def test_text_shows_summary_counts(result):
    out = render_rename_text(result)
    assert "renamed: 1" in out
    assert "skipped: 1" in out
    assert "conflicts: 1" in out


def test_json_structure(result):
    data = json.loads(render_rename_json(result))
    assert "summary" in data
    assert "ops" in data
    assert data["summary"]["renamed"] == 1
    assert data["summary"]["skipped"] == 1
    assert data["summary"]["conflicts"] == 1


def test_json_ops_have_required_fields(result):
    data = json.loads(render_rename_json(result))
    for op in data["ops"]:
        assert "old_key" in op
        assert "new_key" in op
        assert "status" in op
