"""Integration: parse a real file, group it, render output."""
import os
import tempfile
from patchwork_env.parser import parse_env_file
from patchwork_env.grouper import group_env
from patchwork_env.report_grouper import render_group_text, render_group_json
import json


def _write(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_parse_and_group_file():
    path = _write(
        "DB_HOST=localhost\nDB_PORT=5432\nDB_NAME=app\nAPP_ENV=prod\nAPP_DEBUG=false\nSECRET=shh\n"
    )
    try:
        env = parse_env_file(path)
        result = group_env(env)
        assert "DB" in result.groups
        assert "APP" in result.groups
        assert "SECRET" in result.ungrouped
    finally:
        os.unlink(path)


def test_text_render_from_file():
    path = _write("DB_HOST=h\nDB_PORT=5\nSTAND=alone\n")
    try:
        env = parse_env_file(path)
        result = group_env(env)
        text = render_group_text(result)
        assert "DB" in text
    finally:
        os.unlink(path)


def test_json_render_total_keys():
    path = _write("X_A=1\nX_B=2\nY_A=3\nY_B=4\nLONE=5\n")
    try:
        env = parse_env_file(path)
        result = group_env(env)
        data = json.loads(render_group_json(result))
        assert data["total_keys"] == 5
    finally:
        os.unlink(path)
