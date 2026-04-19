"""Integration: parse real files then run multi-diff."""
import os
import tempfile
import json
from patchwork_env.parser import parse_env_file
from patchwork_env.differ_multi import diff_multi
from patchwork_env.report_differ_multi import render_multi_text, render_multi_json


def _write(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    f.write(content)
    f.flush()
    f.close()
    return f.name


def test_parse_and_multi_diff():
    base = _write("A=1\nB=2\nC=3\n")
    dev = _write("A=1\nB=changed\nD=new\n")
    staging = _write("A=1\nB=2\nC=3\nEXTRA=yes\n")
    try:
        b = parse_env_file(base)
        targets = {
            "dev": parse_env_file(dev),
            "staging": parse_env_file(staging),
        }
        result = diff_multi(b, targets, base_label="base")
        assert "dev" in result.labels()
        assert "staging" in result.labels()
        dev_changes = result.changed_in("dev")
        assert any(e.key == "B" for e in dev_changes)
    finally:
        for p in [base, dev, staging]:
            os.unlink(p)


def test_json_output_round_trip():
    base = _write("X=hello\nY=world\n")
    other = _write("X=hello\nY=earth\n")
    try:
        b = parse_env_file(base)
        o = parse_env_file(other)
        result = diff_multi(b, {"other": o})
        raw = render_multi_json(result)
        data = json.loads(raw)
        assert data["diffs"]["other"]
        keys = [e["key"] for e in data["diffs"]["other"]]
        assert "Y" in keys
    finally:
        os.unlink(base)
        os.unlink(other)


def test_text_render_from_files():
    base = _write("K=1\n")
    alt = _write("K=2\n")
    try:
        b = parse_env_file(base)
        a = parse_env_file(alt)
        result = diff_multi(b, {"alt": a})
        text = render_multi_text(result)
        assert "alt" in text
        assert "K" in text
    finally:
        os.unlink(base)
        os.unlink(alt)
