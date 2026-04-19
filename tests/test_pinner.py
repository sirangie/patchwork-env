import json
import pytest
from patchwork_env.pinner import pin_env, PinEntry, PinResult
from patchwork_env.report_pinner import render_pin_text, render_pin_json


BASE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}
PINS = {"APP_ENV": "production", "DB_PORT": "5432"}


def test_pin_overrides_value():
    result = pin_env(BASE_ENV, {"APP_ENV": "production"})
    assert result.env["APP_ENV"] == "production"


def test_pin_preserves_other_keys():
    result = pin_env(BASE_ENV, PINS)
    assert result.env["DB_HOST"] == "localhost"


def test_pinned_keys_listed():
    result = pin_env(BASE_ENV, PINS)
    assert set(result.pinned_keys) == {"APP_ENV", "DB_PORT"}


def test_no_block_without_incoming():
    result = pin_env(BASE_ENV, PINS)
    assert result.blocked_count == 0


def test_block_detected_when_incoming_differs():
    incoming = {"APP_ENV": "staging", "DB_PORT": "5432"}
    result = pin_env(BASE_ENV, PINS, incoming=incoming)
    blocked = [e for e in result.entries if e.blocked]
    assert len(blocked) == 1
    assert blocked[0].key == "APP_ENV"
    assert blocked[0].attempted_value == "staging"


def test_no_block_when_incoming_matches_pin():
    incoming = {"APP_ENV": "production"}
    result = pin_env(BASE_ENV, {"APP_ENV": "production"}, incoming=incoming)
    assert result.blocked_count == 0


def test_pin_adds_new_key_not_in_base():
    result = pin_env({}, {"NEW_KEY": "value"})
    assert result.env["NEW_KEY"] == "value"


def test_render_text_contains_header():
    result = pin_env(BASE_ENV, PINS)
    text = render_pin_text(result)
    assert "Pin Report" in text


def test_render_text_shows_blocked():
    incoming = {"APP_ENV": "staging"}
    result = pin_env(BASE_ENV, {"APP_ENV": "production"}, incoming=incoming)
    text = render_pin_text(result)
    assert "BLOCKED" in text


def test_render_text_shows_values_when_requested():
    result = pin_env(BASE_ENV, {"APP_ENV": "production"})
    text = render_pin_text(result, show_values=True)
    assert "production" in text


def test_render_json_structure():
    result = pin_env(BASE_ENV, PINS)
    data = json.loads(render_pin_json(result))
    assert "pinned_count" in data
    assert "blocked_count" in data
    assert isinstance(data["entries"], list)


def test_render_json_entry_fields():
    result = pin_env(BASE_ENV, {"APP_ENV": "production"})
    data = json.loads(render_pin_json(result))
    entry = data["entries"][0]
    assert entry["key"] == "APP_ENV"
    assert entry["pinned_value"] == "production"
    assert "blocked" in entry
