"""Tests for patchwork_env.report_tagger."""
import json
import pytest
from patchwork_env.tagger import tag_env
from patchwork_env.report_tagger import render_tag_text, render_tag_json


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "key123",
    "STANDALONE": "value",
}

RULES = {"database": ["DB_"], "aws": ["AWS_"]}


@pytest.fixture
def result():
    return tag_env(ENV, RULES)


def test_text_contains_header(result):
    out = render_tag_text(result)
    assert "Tag Report" in out


def test_text_shows_total_keys(result):
    out = render_tag_text(result)
    assert "4" in out


def test_text_shows_tag_names(result):
    out = render_tag_text(result)
    assert "[database]" in out
    assert "[aws]" in out


def test_text_shows_untagged(result):
    out = render_tag_text(result)
    assert "untagged" in out
    assert "STANDALONE" in out


def test_text_hides_values_by_default(result):
    out = render_tag_text(result)
    assert "localhost" not in out


def test_text_shows_values_when_requested(result):
    out = render_tag_text(result, show_values=True)
    assert "localhost" in out


def test_json_total_keys(result):
    data = json.loads(render_tag_json(result))
    assert data["total_keys"] == 4


def test_json_tag_map_present(result):
    data = json.loads(render_tag_json(result))
    assert "database" in data["tag_map"]
    assert "aws" in data["tag_map"]


def test_json_entries_have_key_and_tags(result):
    data = json.loads(render_tag_json(result))
    for entry in data["entries"]:
        assert "key" in entry
        assert "tags" in entry
