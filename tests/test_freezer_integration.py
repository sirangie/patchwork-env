"""Integration: parse a real .env file, freeze it, mutate, check."""
import pathlib
import tempfile
from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.freezer import freeze_env, check_frozen
from patchwork_env.report_freezer import render_freeze_text, render_freeze_json
import json


def _write(tmp_path: pathlib.Path, name: str, content: str) -> pathlib.Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_parse_freeze_no_violations(tmp_path):
    p = _write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    env = parse_env_file(str(p))
    frozen = freeze_env(env)
    result = check_frozen(frozen, env)
    assert result.ok


def test_parse_freeze_detects_mutation(tmp_path):
    p = _write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    env = parse_env_file(str(p))
    frozen = freeze_env(env)
    mutated = dict(env)
    mutated["DB_PORT"] = "9999"
    result = check_frozen(frozen, mutated)
    assert not result.ok
    assert "DB_PORT" in result.violated_keys


def test_text_render_from_file(tmp_path):
    p = _write(tmp_path, ".env", "HOST=prod\nPORT=443\n")
    env = parse_env_file(str(p))
    frozen = freeze_env(env)
    current = dict(env)
    current["PORT"] = "80"
    result = check_frozen(frozen, current)
    text = render_freeze_text(result)
    assert "CHANGED" in text
    assert "PORT" in text


def test_json_round_trip(tmp_path):
    p = _write(tmp_path, ".env", "A=1\nB=2\nC=3\n")
    env = parse_env_file(str(p))
    frozen = freeze_env(env)
    result = check_frozen(frozen, env)
    data = json.loads(render_freeze_json(result))
    assert data["frozen_key_count"] == 3
    assert data["ok"] is True
