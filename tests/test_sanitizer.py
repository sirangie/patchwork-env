"""Tests for patchwork_env.sanitizer and report_sanitizer."""
import json

import pytest

from patchwork_env.sanitizer import sanitize_env, SanitizeOp, SanitizeResult
from patchwork_env.report_sanitizer import render_sanitize_text, render_sanitize_json


# ---------------------------------------------------------------------------
# sanitize_env core behaviour
# ---------------------------------------------------------------------------

def test_clean_value_unchanged():
    env = {"KEY": "clean_value"}
    result = sanitize_env(env)
    assert result.env["KEY"] == "clean_value"
    assert result.unchanged_count == 1
    assert result.changed_count == 0


def test_strips_surrounding_whitespace():
    env = {"KEY": "  hello  "}
    result = sanitize_env(env)
    assert result.env["KEY"] == "hello"
    assert result.changed_count == 1
    assert "stripped surrounding whitespace" in result.ops[0].reasons


def test_no_strip_when_disabled():
    env = {"KEY": "  hello  "}
    result = sanitize_env(env, strip_surrounding_whitespace=False)
    assert result.env["KEY"] == "  hello  "
    assert result.changed_count == 0


def test_removes_control_characters():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env)
    assert "\x00" not in result.env["KEY"]
    assert result.changed_count == 1
    assert any("control" in r for r in result.ops[0].reasons)


def test_collapses_newlines():
    env = {"KEY": "line1\nline2"}
    result = sanitize_env(env)
    assert "\n" not in result.env["KEY"]
    assert result.env["KEY"] == "line1 line2"
    assert any("newline" in r for r in result.ops[0].reasons)


def test_custom_newline_replacement():
    env = {"KEY": "a\nb"}
    result = sanitize_env(env, newline_replacement="|")
    assert result.env["KEY"] == "a|b"


def test_max_length_truncates():
    env = {"KEY": "abcdefgh"}
    result = sanitize_env(env, max_length=4)
    assert result.env["KEY"] == "abcd"
    assert any("truncated" in r for r in result.ops[0].reasons)


def test_max_length_not_exceeded_skips():
    env = {"KEY": "abc"}
    result = sanitize_env(env, max_length=10)
    assert result.changed_count == 0


def test_changed_keys_list():
    env = {"A": "  spaces  ", "B": "clean"}
    result = sanitize_env(env)
    assert "A" in result.changed_keys
    assert "B" not in result.changed_keys


def test_multiple_reasons_accumulated():
    env = {"KEY": "  val\x01ue\n  "}
    result = sanitize_env(env)
    reasons = result.ops[0].reasons
    assert len(reasons) >= 2


# ---------------------------------------------------------------------------
# render_sanitize_text
# ---------------------------------------------------------------------------

def test_text_contains_header():
    result = sanitize_env({"K": "v"})
    text = render_sanitize_text(result)
    assert "Sanitize Report" in text


def test_text_shows_changed_marker():
    result = sanitize_env({"K": "  hi  "})
    text = render_sanitize_text(result)
    assert "~ K" in text


def test_text_shows_unchanged_marker():
    result = sanitize_env({"K": "clean"})
    text = render_sanitize_text(result)
    assert "= K" in text


def test_text_shows_values_when_requested():
    result = sanitize_env({"K": "  hi  "})
    text = render_sanitize_text(result, show_values=True)
    assert "->" in text


# ---------------------------------------------------------------------------
# render_sanitize_json
# ---------------------------------------------------------------------------

def test_json_structure():
    result = sanitize_env({"A": "  x  ", "B": "ok"})
    data = json.loads(render_sanitize_json(result))
    assert "summary" in data
    assert "ops" in data
    assert data["summary"]["changed"] == 1
    assert data["summary"]["unchanged"] == 1


def test_json_op_fields_for_changed_key():
    result = sanitize_env({"K": "  v  "})
    data = json.loads(render_sanitize_json(result))
    op = data["ops"][0]
    assert op["changed"] is True
    assert op["original"] is not None
    assert op["sanitized"] is not None


def test_json_op_fields_for_clean_key():
    result = sanitize_env({"K": "clean"})
    data = json.loads(render_sanitize_json(result))
    op = data["ops"][0]
    assert op["changed"] is False
    assert op["original"] is None
    assert op["sanitized"] is None
