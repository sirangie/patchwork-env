"""Tests for patchwork_env.report_differ_keys."""
import json
import pytest
from patchwork_env.differ_keys import diff_keys
from patchwork_env.report_differ_keys import render_key_diff_text, render_key_diff_json


BASE = {"A": "1", "B": "2", "SHARED": "x"}
TARGET = {"C": "3", "D": "4", "SHARED": "x"}


@pytest.fixture
def result():
    return diff_keys(BASE, TARGET, base_label="prod", target_label="dev")


def test_text_contains_labels(result):
    out = render_key_diff_text(result)
    assert "prod" in out
    assert "dev" in out


def test_text_shows_only_in_base(result):
    out = render_key_diff_text(result)
    assert "- A" in out
    assert "- B" in out


def test_text_shows_only_in_target(result):
    out = render_key_diff_text(result)
    assert "+ C" in out
    assert "+ D" in out


def test_text_no_diff_message_when_identical():
    r = diff_keys({"X": "1"}, {"X": "2"})
    out = render_key_diff_text(r)
    assert "No key-set differences" in out


def test_text_shared_hidden_by_default(result):
    out = render_key_diff_text(result)
    assert "= SHARED" not in out


def test_text_shared_shown_when_requested(result):
    out = render_key_diff_text(result, show_shared=True)
    assert "= SHARED" in out


def test_json_round_trip(result):
    raw = render_key_diff_json(result)
    data = json.loads(raw)
    assert data["base_label"] == "prod"
    assert data["target_label"] == "dev"
    assert "A" in data["only_in_base"]
    assert "C" in data["only_in_target"]
    assert "SHARED" in data["shared"]
    assert data["has_differences"] is True


def test_json_coverage_field(result):
    data = json.loads(render_key_diff_json(result))
    assert 0.0 <= data["coverage"] <= 1.0
