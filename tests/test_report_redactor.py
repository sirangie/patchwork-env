import json
import pytest
from patchwork_env.redactor import redact_env
from patchwork_env.report_redactor import render_redact_text, render_redact_json


@pytest.fixture
def result():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp", "API_KEY": "key123"}
    return redact_env(env)


def test_text_contains_header(result):
    out = render_redact_text(result)
    assert "Redaction Report" in out


def test_text_shows_totals(result):
    out = render_redact_text(result)
    assert "Total keys" in out
    assert "3" in out


def test_text_lists_redacted_keys(result):
    out = render_redact_text(result)
    assert "DB_PASSWORD" in out
    assert "API_KEY" in out


def test_text_safe_value_visible(result):
    out = render_redact_text(result)
    assert "myapp" in out


def test_text_no_redacted_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    out = render_redact_text(result)
    assert "No keys were redacted" in out


def test_json_structure(result):
    out = render_redact_json(result)
    data = json.loads(out)
    assert "total" in data
    assert "redacted_count" in data
    assert "redacted_keys" in data
    assert "env" in data


def test_json_redacted_count(result):
    data = json.loads(render_redact_json(result))
    assert data["redacted_count"] == 2


def test_json_env_values_masked(result):
    data = json.loads(render_redact_json(result))
    assert data["env"]["DB_PASSWORD"] == "***REDACTED***"
