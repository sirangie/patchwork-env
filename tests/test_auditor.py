"""Tests for patchwork_env.auditor."""
import json
from pathlib import Path

import pytest

from patchwork_env.auditor import record_diff, record_sync, read_audit_log
from patchwork_env.differ import DiffEntry


@pytest.fixture()
def audit_path(tmp_path):
    return str(tmp_path / "audit.jsonl")


def _entry(key, status, old=None, new=None):
    return DiffEntry(key=key, status=status, old_value=old, new_value=new)


def test_record_diff_creates_file(audit_path):
    record_diff([], "a.env", "b.env", audit_file=audit_path)
    assert Path(audit_path).exists()


def test_record_diff_event_fields(audit_path):
    entries = [
        _entry("FOO", "changed", "1", "2"),
        _entry("BAR", "unchanged", "x", "x"),
        _entry("BAZ", "added", None, "3"),
    ]
    record_diff(entries, "src.env", "tgt.env", audit_file=audit_path)
    events = read_audit_log(audit_path)
    assert len(events) == 1
    ev = events[0]
    assert ev["event"] == "diff"
    assert ev["source"] == "src.env"
    assert ev["target"] == "tgt.env"
    # unchanged should be filtered out
    keys = [c["key"] for c in ev["changes"]]
    assert "FOO" in keys
    assert "BAZ" in keys
    assert "BAR" not in keys


def test_record_sync_event_fields(audit_path):
    record_sync(["FOO", "BAR"], ["SECRET"], "prod.env", audit_file=audit_path)
    events = read_audit_log(audit_path)
    assert len(events) == 1
    ev = events[0]
    assert ev["event"] == "sync"
    assert ev["applied"] == ["FOO", "BAR"]
    assert ev["skipped"] == ["SECRET"]
    assert ev["target"] == "prod.env"


def test_multiple_events_appended(audit_path):
    record_diff([], "a", "b", audit_file=audit_path)
    record_sync([], [], "b", audit_file=audit_path)
    record_diff([], "c", "d", audit_file=audit_path)
    events = read_audit_log(audit_path)
    assert len(events) == 3
    assert events[0]["event"] == "diff"
    assert events[1]["event"] == "sync"
    assert events[2]["event"] == "diff"


def test_read_missing_file_returns_empty(tmp_path):
    result = read_audit_log(str(tmp_path / "nonexistent.jsonl"))
    assert result == []


def test_timestamp_present(audit_path):
    record_diff([], "a", "b", audit_file=audit_path)
    events = read_audit_log(audit_path)
    assert "timestamp" in events[0]
    assert events[0]["timestamp"].endswith("+00:00")
