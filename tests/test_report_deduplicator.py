import json
import pytest
from patchwork_env.deduplicator import deduplicate_env, DedupeOp, DedupeResult
from patchwork_env.report_deduplicator import render_dedupe_text, render_dedupe_json


@pytest.fixture
def clean_result():
    return deduplicate_env([("A", "1"), ("B", "2")])


@pytest.fixture
def dirty_result():
    pairs = [("SECRET", "old"), ("SECRET", "new"), ("SAFE", "val")]
    return deduplicate_env(pairs, strategy="last")


def test_text_contains_header(clean_result):
    out = render_dedupe_text(clean_result)
    assert "Deduplication" in out


def test_text_clean_message(clean_result):
    out = render_dedupe_text(clean_result)
    assert "No duplicate" in out


def test_text_shows_duplicate_key(dirty_result):
    out = render_dedupe_text(dirty_result)
    assert "SECRET" in out


def test_text_shows_count(dirty_result):
    out = render_dedupe_text(dirty_result)
    assert "1" in out


def test_text_shows_values_when_requested(dirty_result):
    out = render_dedupe_text(dirty_result, show_values=True)
    assert "kept" in out
    assert "dropped" in out


def test_text_hides_values_by_default(dirty_result):
    out = render_dedupe_text(dirty_result, show_values=False)
    assert "kept" not in out


def test_json_clean_flag(clean_result):
    data = json.loads(render_dedupe_json(clean_result))
    assert data["clean"] is True


def test_json_dirty_flag(dirty_result):
    data = json.loads(render_dedupe_json(dirty_result))
    assert data["clean"] is False


def test_json_ops_structure(dirty_result):
    data = json.loads(render_dedupe_json(dirty_result))
    op = data["ops"][0]
    assert "key" in op
    assert "kept_value" in op
    assert "dropped_values" in op
    assert "strategy" in op


def test_json_env_present(dirty_result):
    data = json.loads(render_dedupe_json(dirty_result))
    assert "env" in data
    assert data["env"]["SECRET"] == "new"
