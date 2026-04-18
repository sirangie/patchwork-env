"""Tests for the CLI layer."""

import json
from pathlib import Path
import pytest

from patchwork_env.cli import build_parser, cmd_diff, cmd_sync


@pytest.fixture()
def env_files(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("APP=hello\nSECRET=old\nONLY_BASE=yes\n")
    target.write_text("APP=hello\nSECRET=new\nONLY_TARGET=yes\n")
    return base, target


def _parse(args_list):
    parser = build_parser()
    return parser.parse_args(args_list)


def test_diff_text(env_files, capsys):
    base, target = env_files
    args = _parse(["diff", str(base), str(target)])
    args.func(args)
    out = capsys.readouterr().out
    assert "SECRET" in out
    assert "ONLY_BASE" in out
    assert "ONLY_TARGET" in out


def test_diff_mask(env_files, capsys):
    base, target = env_files
    args = _parse(["diff", str(base), str(target), "--mask"])
    args.func(args)
    out = capsys.readouterr().out
    assert "old" not in out
    assert "new" not in out


def test_diff_json(env_files, capsys):
    base, target = env_files
    args = _parse(["diff", str(base), str(target), "--format", "json"])
    args.func(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    keys = {entry["key"] for entry in data}
    assert "SECRET" in keys


def test_sync_writes_file(env_files, tmp_path, capsys):
    base, target = env_files
    out_file = tmp_path / ".env.out"
    args = _parse(["sync", str(base), str(target), "--output", str(out_file)])
    args.func(args)
    content = out_file.read_text()
    assert "SECRET=new" in content
    assert "ONLY_TARGET=yes" in content


def test_sync_no_overwrite(env_files, tmp_path):
    base, target = env_files
    out_file = tmp_path / ".env.out"
    args = _parse(["sync", str(base), str(target), "--output", str(out_file), "--no-overwrite"])
    args.func(args)
    content = out_file.read_text()
    assert "SECRET=old" in content


def test_sync_no_add(env_files, tmp_path):
    base, target = env_files
    out_file = tmp_path / ".env.out"
    args = _parse(["sync", str(base), str(target), "--output", str(out_file), "--no-add"])
    args.func(args)
    content = out_file.read_text()
    assert "ONLY_TARGET" not in content
