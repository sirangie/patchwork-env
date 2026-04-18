"""Tests for report_export module."""
import json
import pytest
from patchwork_env.report_export import render_export_text, render_export_json


@pytest.fixture()
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
    }


def test_render_text_contains_format(sample_env):
    out = render_export_text(sample_env, "shell")
    assert "shell" in out


def test_render_text_contains_key_count(sample_env):
    out = render_export_text(sample_env, "shell")
    assert "3" in out


def test_render_text_lists_all_keys(sample_env):
    out = render_export_text(sample_env, "docker")
    for key in sample_env:
        assert key in out


def test_render_text_keys_sorted(sample_env):
    out = render_export_text(sample_env, "shell")
    key_lines = [l.strip() for l in out.splitlines() if l.strip() in sample_env]
    assert key_lines == sorted(sample_env.keys())


def test_render_text_values_not_present(sample_env):
    out = render_export_text(sample_env, "shell")
    for val in sample_env.values():
        assert val not in out


def test_render_json_structure(sample_env):
    out = render_export_json(sample_env, "json")
    data = json.loads(out)
    assert data["format"] == "json"
    assert data["key_count"] == 3
    assert isinstance(data["keys"], list)


def test_render_json_keys_sorted(sample_env):
    out = render_export_json(sample_env, "shell")
    data = json.loads(out)
    assert data["keys"] == sorted(sample_env.keys())


def test_render_json_no_values(sample_env):
    out = render_export_json(sample_env, "docker")
    for val in sample_env.values():
        assert val not in out


def test_empty_env():
    out = render_export_text({}, "shell")
    assert "0" in out
    data = json.loads(render_export_json({}, "shell"))
    assert data["key_count"] == 0
    assert data["keys"] == []
