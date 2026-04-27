"""Tests for patchwork_env.archiver."""
import json
from pathlib import Path

import pytest

from patchwork_env.archiver import (
    ArchiveResult,
    archive_files,
    load_archive,
    restore_archive,
    save_archive,
)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_archive_names_match_filenames(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_path, "prod.env", "FOO=prod_bar\n")
    result = archive_files([a, b])
    assert result.names == ["dev.env", "prod.env"]


def test_archive_total_keys(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_path, "prod.env", "FOO=prod_bar\nEXTRA=1\n")
    result = archive_files([a, b])
    assert result.total_keys == 4


def test_archive_get_entry(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\n")
    result = archive_files([a])
    entry = result.get("dev.env")
    assert entry is not None
    assert entry.env["FOO"] == "bar"


def test_archive_get_missing_returns_none(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\n")
    result = archive_files([a])
    assert result.get("nope.env") is None


def test_save_and_load_roundtrip(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\nSECRET=xyz\n")
    result = archive_files([a])
    archive_path = tmp_path / "archive.json"
    save_archive(result, archive_path)
    loaded = load_archive(archive_path)
    assert loaded.names == ["dev.env"]
    assert loaded.get("dev.env").env["SECRET"] == "xyz"


def test_save_produces_valid_json(tmp_path):
    a = _write(tmp_path, "dev.env", "K=V\n")
    result = archive_files([a])
    archive_path = tmp_path / "archive.json"
    save_archive(result, archive_path)
    payload = json.loads(archive_path.read_text())
    assert "entries" in payload
    assert "source_paths" in payload


def test_restore_writes_files(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\n")
    result = archive_files([a])
    restore_dir = tmp_path / "restored"
    written = restore_archive(result, restore_dir)
    assert len(written) == 1
    assert (restore_dir / "dev.env").exists()


def test_restore_values_preserved(tmp_path):
    a = _write(tmp_path, "dev.env", "FOO=bar\nBAZ=qux\n")
    result = archive_files([a])
    restore_dir = tmp_path / "restored"
    restore_archive(result, restore_dir)
    from patchwork_env.parser import parse_env_file
    restored_env = parse_env_file(restore_dir / "dev.env")
    assert restored_env["FOO"] == "bar"
    assert restored_env["BAZ"] == "qux"


def test_source_paths_recorded(tmp_path):
    a = _write(tmp_path, "dev.env", "X=1\n")
    result = archive_files([a])
    assert str(a) in result.source_paths
