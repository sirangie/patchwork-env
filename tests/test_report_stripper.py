"""tests for report_stripper.py"""
import json
import pytest
from patchwork_env.stripper import strip_env
from patchwork_env.report_stripper import render_strip_text, render_strip_json


ENV = {"APP_NAME": "myapp", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}


@pytest.fixture
def result():
    return strip_env(ENV, keys=["DB_PASSWORD"])


def test_text_contains_header(result):
    assert "Strip Report" in render_strip_text(result)


def test_text_shows_removed_count(result):
    text = render_strip_text(result)
    assert "Keys removed      : 1" in text


def test_text_lists_removed_key(result):
    text = render_strip_text(result)
    assert "DB_PASSWORD" in text


def test_text_shows_reason(result):
    text = render_strip_text(result)
    assert "explicit" in text


def test_text_no_removal_message():
    r = strip_env(ENV)
    assert "No keys removed" in render_strip_text(r)


def test_json_structure(result):
    data = json.loads(render_strip_json(result))
    assert "total_before" in data
    assert "removed_count" in data
    assert "remaining_count" in data
    assert isinstance(data["removed"], list)


def test_json_removed_entry(result):
    data = json.loads(render_strip_json(result))
    keys = [e["key"] for e in data["removed"]]
    assert "DB_PASSWORD" in keys


def test_json_counts_consistent(result):
    data = json.loads(render_strip_json(result))
    assert data["total_before"] == data["removed_count"] + data["remaining_count"]
