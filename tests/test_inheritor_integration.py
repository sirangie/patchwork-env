"""Integration tests: parse .env files then run inherit_env."""
import pathlib
import pytest
from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.inheritor import inherit_env
from patchwork_env.report_inheritor import render_inherit_text, render_inherit_json
import json


def _write(tmp_path: pathlib.Path, name: str, content: str) -> pathlib.Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_parse_and_inherit_files(tmp_path):
    parent_file = _write(tmp_path, "parent.env", "DB_HOST=prod\nDB_PORT=5432\nSECRET=abc\n")
    child_file = _write(tmp_path, "child.env", "DB_HOST=local\nAPP=web\n")

    parent = parse_env_file(str(parent_file))
    child = parse_env_file(str(child_file))
    result = inherit_env(parent, child)

    assert result.env["DB_HOST"] == "local"
    assert result.env["DB_PORT"] == "5432"
    assert result.env["APP"] == "web"


def test_serialize_inherited_env(tmp_path):
    parent_file = _write(tmp_path, "parent.env", "TOKEN=xyz\nTIMEOUT=30\n")
    child_file = _write(tmp_path, "child.env", "TIMEOUT=60\nDEBUG=true\n")

    parent = parse_env_file(str(parent_file))
    child = parse_env_file(str(child_file))
    result = inherit_env(parent, child)

    serialized = serialize_env(result.env)
    assert "TOKEN=xyz" in serialized
    assert "TIMEOUT=60" in serialized
    assert "DEBUG=true" in serialized


def test_text_render_from_files(tmp_path):
    parent_file = _write(tmp_path, "parent.env", "HOST=prod\nPORT=80\n")
    child_file = _write(tmp_path, "child.env", "HOST=local\n")

    parent = parse_env_file(str(parent_file))
    child = parse_env_file(str(child_file))
    result = inherit_env(parent, child)

    text = render_inherit_text(result)
    assert "Inherit Report" in text
    assert "PORT" in text


def test_json_round_trip(tmp_path):
    parent_file = _write(tmp_path, "parent.env", "A=1\nB=2\n")
    child_file = _write(tmp_path, "child.env", "A=99\nC=3\n")

    parent = parse_env_file(str(parent_file))
    child = parse_env_file(str(child_file))
    result = inherit_env(parent, child)

    data = json.loads(render_inherit_json(result))
    assert data["inherited_count"] >= 1
    keys_in_ops = [op["key"] for op in data["ops"]]
    assert "A" in keys_in_ops
    assert "B" in keys_in_ops
    assert "C" in keys_in_ops
