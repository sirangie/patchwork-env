"""Integration tests: parse a real .env file and diff against a schema."""
import json
import pathlib
import pytest
from patchwork_env.parser import parse_env_file
from patchwork_env.differ_schema import SchemaField, diff_schema
from patchwork_env.report_differ_schema import render_schema_diff_text, render_schema_diff_json


def _write(tmp_path: pathlib.Path, name: str, content: str) -> pathlib.Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_parse_and_diff_clean(tmp_path):
    env_file = _write(tmp_path, ".env", "HOST=localhost\nPORT=5432\nDEBUG=false\n")
    env = parse_env_file(str(env_file))
    schema = [
        SchemaField("HOST", required=True),
        SchemaField("PORT", required=True),
        SchemaField("DEBUG", required=False),
    ]
    result = diff_schema(env, schema)
    assert result.ok is True
    assert len(result.ok_keys) == 3


def test_parse_and_diff_missing_required(tmp_path):
    env_file = _write(tmp_path, ".env", "HOST=localhost\n")
    env = parse_env_file(str(env_file))
    schema = [
        SchemaField("HOST", required=True),
        SchemaField("SECRET_KEY", required=True),
    ]
    result = diff_schema(env, schema)
    assert result.ok is False
    assert result.missing_required[0].key == "SECRET_KEY"


def test_text_render_from_file(tmp_path):
    env_file = _write(tmp_path, ".env", "A=1\nB=2\n")
    env = parse_env_file(str(env_file))
    schema = [SchemaField("A"), SchemaField("B"), SchemaField("C", required=False)]
    result = diff_schema(env, schema)
    text = render_schema_diff_text(result)
    assert "A" in text
    assert "B" in text
    assert "C" in text


def test_json_round_trip(tmp_path):
    env_file = _write(tmp_path, ".env", "X=hello\n")
    env = parse_env_file(str(env_file))
    schema = [SchemaField("X"), SchemaField("Y", required=False, default="world")]
    result = diff_schema(env, schema)
    raw = render_schema_diff_json(result)
    data = json.loads(raw)
    assert data["ok"] is True
    assert any(e["key"] == "Y" for e in data["entries"])
    defaults = {e["key"]: e["default"] for e in data["entries"]}
    assert defaults["Y"] == "world"
