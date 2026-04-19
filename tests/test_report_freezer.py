import json
import pytest
from patchwork_env.freezer import freeze_env, check_frozen
from patchwork_env.report_freezer import render_freeze_text, render_freeze_json


BASE = {"API_KEY": "secret", "HOST": "localhost", "PORT": "8080"}


@pytest.fixture
def clean_result():
    frozen = freeze_env(BASE)
    return check_frozen(frozen, dict(BASE))


@pytest.fixture
def dirty_result():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["PORT"] = "9999"
    del current["HOST"]
    return check_frozen(frozen, current)


def test_text_contains_header(clean_result):
    out = render_freeze_text(clean_result)
    assert "Freeze Check" in out


def test_text_ok_status(clean_result):
    out = render_freeze_text(clean_result)
    assert "OK" in out


def test_text_violation_status(dirty_result):
    out = render_freeze_text(dirty_result)
    assert "VIOLATIONS FOUND" in out


def test_text_shows_changed_tag(dirty_result):
    out = render_freeze_text(dirty_result)
    assert "CHANGED" in out


def test_text_shows_removed_tag(dirty_result):
    out = render_freeze_text(dirty_result)
    assert "REMOVED" in out


def test_text_hides_values_by_default(dirty_result):
    out = render_freeze_text(dirty_result)
    assert "9999" not in out


def test_text_shows_values_when_requested(dirty_result):
    out = render_freeze_text(dirty_result, show_values=True)
    assert "9999" in out


def test_json_ok_field(clean_result):
    data = json.loads(render_freeze_json(clean_result))
    assert data["ok"] is True
    assert data["violation_count"] == 0


def test_json_violations_list(dirty_result):
    data = json.loads(render_freeze_json(dirty_result))
    assert data["ok"] is False
    keys = [v["key"] for v in data["violations"]]
    assert "PORT" in keys
    assert "HOST" in keys
