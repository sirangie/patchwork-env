"""Tests for patchwork_env.report_composer."""
import json

import pytest

from patchwork_env.composer import compose_envs
from patchwork_env.report_composer import render_compose_text, render_compose_json


A = {"HOST": "localhost", "PORT": "5432"}
B = {"HOST": "prod.db", "SECRET": "s3cr3t"}


@pytest.fixture()
def result():
    return compose_envs([("base", A), ("prod", B)], strategy="last")


def test_text_contains_header(result):
    text = render_compose_text(result)
    assert "Compose Result" in text


def test_text_shows_source_labels(result):
    text = render_compose_text(result)
    assert "base" in text
    assert "prod" in text


def test_text_shows_total_keys(result):
    text = render_compose_text(result)
    assert str(result.total_keys) in text


def test_text_hides_values_by_default(result):
    text = render_compose_text(result)
    assert "s3cr3t" not in text
    assert "localhost" not in text


def test_text_shows_values_when_requested(result):
    text = render_compose_text(result, show_values=True)
    assert "localhost" in text or "prod.db" in text


def test_text_shows_source_annotation(result):
    text = render_compose_text(result, show_source=True)
    assert "[prod]" in text or "[base]" in text


def test_text_empty_result():
    empty = compose_envs([])
    text = render_compose_text(empty)
    assert "(no keys)" in text


def test_json_has_entries_key(result):
    data = json.loads(render_compose_json(result))
    assert "entries" in data


def test_json_entries_have_source_field(result):
    data = json.loads(render_compose_json(result))
    for entry in data["entries"]:
        assert "source" in entry
        assert entry["source"] in ("base", "prod")


def test_json_total_keys_matches(result):
    data = json.loads(render_compose_json(result))
    assert data["total_keys"] == result.total_keys
    assert len(data["entries"]) == result.total_keys
