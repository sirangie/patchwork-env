import json
from patchwork_env.validator import validate_env
from patchwork_env.report import render_validation_text, render_validation_json

TEMPLATE = {"DB": "postgres", "SECRET": "x", "OPT": ""}


def test_render_text_clean():
    env = {"DB": "postgres", "SECRET": "abc", "OPT": "1"}
    result = validate_env(env, TEMPLATE)
    text = render_validation_text(result)
    assert "passed" in text


def test_render_text_with_errors():
    env = {"OPT": "1"}
    result = validate_env(env, TEMPLATE)
    text = render_validation_text(result)
    assert "FAILED" in text
    assert "DB" in text
    assert "SECRET" in text


def test_render_text_warnings_only():
    env = {"DB": "x", "SECRET": "y"}
    result = validate_env(env, TEMPLATE)
    text = render_validation_text(result)
    assert "PASSED" in text
    assert "OPT" in text


def test_render_json_structure():
    env = {"SECRET": "y"}
    result = validate_env(env, TEMPLATE)
    data = json.loads(render_validation_json(result))
    assert "ok" in data
    assert "errors" in data
    assert "warnings" in data
    assert not data["ok"]
    error_keys = [e["key"] for e in data["errors"]]
    assert "DB" in error_keys


def test_render_json_ok():
    env = {"DB": "x", "SECRET": "y", "OPT": "z"}
    result = validate_env(env, TEMPLATE)
    data = json.loads(render_validation_json(result))
    assert data["ok"] is True
    assert data["errors"] == []
