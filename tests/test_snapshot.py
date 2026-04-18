"""Tests for snapshot capture and comparison."""
import json
import os
import pytest
from patchwork_env.snapshot import (
    take_snapshot,
    save_snapshot,
    load_snapshot,
    compare_snapshots,
)
from patchwork_env.report_snapshot import render_snapshot_text, render_snapshot_json


ENV_A = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "DB": "mydb"}


def test_take_snapshot_has_required_fields():
    snap = take_snapshot(ENV_A, label="dev")
    assert snap["label"] == "dev"
    assert "timestamp" in snap
    assert snap["keys"] == sorted(ENV_A.keys())
    assert snap["values"] == ENV_A


def test_save_and_load_roundtrip(tmp_path):
    snap = take_snapshot(ENV_A, label="test")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded["label"] == "test"
    assert loaded["values"] == ENV_A


def test_compare_detects_added():
    old = take_snapshot(ENV_A)
    new = take_snapshot(ENV_B)
    changes = compare_snapshots(old, new)
    statuses = {c["key"]: c["status"] for c in changes}
    assert statuses["DB"] == "added"


def test_compare_detects_removed():
    old = take_snapshot(ENV_A)
    new = take_snapshot(ENV_B)
    changes = compare_snapshots(old, new)
    statuses = {c["key"]: c["status"] for c in changes}
    assert statuses["SECRET"] == "removed"


def test_compare_detects_changed():
    old = take_snapshot(ENV_A)
    new = take_snapshot(ENV_B)
    changes = compare_snapshots(old, new)
    statuses = {c["key"]: c["status"] for c in changes}
    assert statuses["HOST"] == "changed"


def test_compare_no_changes_when_identical():
    snap = take_snapshot(ENV_A)
    changes = compare_snapshots(snap, snap)
    assert changes == []


def test_render_text_no_changes():
    snap = take_snapshot(ENV_A, label="same")
    text = render_snapshot_text(snap, snap, [])
    assert "No changes" in text


def test_render_text_shows_changes():
    old = take_snapshot(ENV_A, label="old")
    new = take_snapshot(ENV_B, label="new")
    changes = compare_snapshots(old, new)
    text = render_snapshot_text(old, new, changes)
    assert "HOST" in text
    assert "change(s)" in text


def test_render_json_structure():
    old = take_snapshot(ENV_A, label="v1")
    new = take_snapshot(ENV_B, label="v2")
    changes = compare_snapshots(old, new)
    data = json.loads(render_snapshot_json(old, new, changes))
    assert data["from"] == "v1"
    assert data["to"] == "v2"
    assert isinstance(data["changes"], list)
    assert data["change_count"] == len(changes)
