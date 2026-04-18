"""Integration: parse two temp env files and compare them."""
import os
import tempfile
from patchwork_env.parser import parse_env_file
from patchwork_env.comparator import compare_envs
from patchwork_env.report_comparator import render_compare_text, render_compare_json
import json


def _write(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_parse_and_compare_files():
    p1 = _write("A=hello\nB=world\n")
    p2 = _write("A=hello\nC=there\n")
    try:
        left = parse_env_file(p1)
        right = parse_env_file(p2)
        result = compare_envs(left, right, left_label=p1, right_label=p2)
        assert not result.is_identical
        assert any(e.key == "B" for e in result.removed)
        assert any(e.key == "C" for e in result.added)
    finally:
        os.unlink(p1)
        os.unlink(p2)


def test_identical_files_report():
    p1 = _write("KEY=value\n")
    p2 = _write("KEY=value\n")
    try:
        result = compare_envs(parse_env_file(p1), parse_env_file(p2))
        text = render_compare_text(result)
        assert "identical" in text.lower()
    finally:
        os.unlink(p1)
        os.unlink(p2)


def test_json_round_trip():
    p1 = _write("X=1\nY=2\n")
    p2 = _write("X=9\nZ=3\n")
    try:
        result = compare_envs(parse_env_file(p1), parse_env_file(p2))
        data = json.loads(render_compare_json(result))
        statuses = {e["key"]: e["status"] for e in data["entries"]}
        assert statuses["X"] == "changed"
        assert statuses["Y"] == "removed"
        assert statuses["Z"] == "added"
    finally:
        os.unlink(p1)
        os.unlink(p2)
