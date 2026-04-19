import pytest
from patchwork_env.normalizer import normalize_env, NormalizeOp
from patchwork_env.report_normalizer import render_normalize_text, render_normalize_json
import json


def test_strip_trailing_whitespace():
    result = normalize_env({"KEY": "  hello  "}, strip_values=True)
    assert result.env["KEY"] == "hello"


def test_no_strip_preserves_whitespace():
    result = normalize_env({"KEY": "  hello  "}, strip_values=False)
    assert result.env["KEY"] == "  hello  "


def test_upper_key_case():
    result = normalize_env({"my_key": "val"}, key_case="upper")
    assert "MY_KEY" in result.env


def test_lower_key_case():
    result = normalize_env({"MY_KEY": "val"}, key_case="lower")
    assert "my_key" in result.env


def test_preserve_key_case():
    result = normalize_env({"My_Key": "val"}, key_case="preserve")
    assert "My_Key" in result.env


def test_changed_count():
    result = normalize_env({"key": "  val  ", "OTHER": "clean"}, key_case="upper")
    # 'key' -> 'KEY' (upper_key) + strip; 'OTHER' already upper + clean
    assert result.changed_count >= 1


def test_unchanged_count():
    result = normalize_env({"KEY": "clean"}, key_case="upper")
    assert result.unchanged_count == 1
    assert result.changed_count == 0


def test_changed_keys_list():
    result = normalize_env({"lower": "val"}, key_case="upper")
    assert "LOWER" in result.changed_keys


def test_render_text_contains_header():
    result = normalize_env({"KEY": "val"})
    text = render_normalize_text(result)
    assert "Normalize Report" in text


def test_render_text_shows_changed_marker():
    result = normalize_env({"lower_key": "  spaced  "}, key_case="upper")
    text = render_normalize_text(result, show_values=True)
    assert "~" in text


def test_render_json_structure():
    result = normalize_env({"KEY": "val"})
    data = json.loads(render_normalize_json(result))
    assert "total" in data
    assert "ops" in data
    assert isinstance(data["ops"], list)


def test_render_json_op_fields():
    result = normalize_env({"KEY": "val"})
    data = json.loads(render_normalize_json(result))
    op = data["ops"][0]
    assert "key" in op
    assert "action" in op
    assert "old_value" in op
    assert "new_value" in op
