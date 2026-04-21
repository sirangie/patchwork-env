"""Tests for patchwork_env.report_rotator."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from patchwork_env.rotator import RotateEntry, RotateResult
from patchwork_env.report_rotator import render_rotate_text, render_rotate_json


def _iso(days_ago: float) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


@pytest.fixture()
def clean_result() -> RotateResult:
    return RotateResult(
        entries=[
            RotateEntry(
                key="SECRET_KEY",
                last_rotated=_iso(10),
                age_days=10.0,
                due=False,
                reason="rotated 10.0 days ago — ok",
            )
        ],
        threshold_days=90,
    )


@pytest.fixture()
def dirty_result() -> RotateResult:
    return RotateResult(
        entries=[
            RotateEntry(
                key="API_TOKEN",
                last_rotated=None,
                age_days=None,
                due=True,
                reason="no rotation timestamp recorded",
            ),
            RotateEntry(
                key="DB_PASSWORD",
                last_rotated=_iso(120),
                age_days=120.0,
                due=True,
                reason="last rotated 120.0 days ago (threshold 90d)",
            ),
        ],
        threshold_days=90,
    )


def test_text_contains_header(clean_result):
    out = render_rotate_text(clean_result)
    assert "Rotation Check" in out


def test_text_clean_message(clean_result):
    out = render_rotate_text(clean_result)
    assert "within rotation policy" in out


def test_text_shows_due_key(dirty_result):
    out = render_rotate_text(dirty_result)
    assert "API_TOKEN" in out
    assert "DB_PASSWORD" in out


def test_text_shows_threshold(dirty_result):
    out = render_rotate_text(dirty_result)
    assert "90" in out


def test_json_clean_flag(clean_result):
    data = json.loads(render_rotate_json(clean_result))
    assert data["clean"] is True
    assert data["due_count"] == 0


def test_json_due_keys_listed(dirty_result):
    data = json.loads(render_rotate_json(dirty_result))
    assert "API_TOKEN" in data["due_keys"]
    assert "DB_PASSWORD" in data["due_keys"]


def test_json_entries_structure(dirty_result):
    data = json.loads(render_rotate_json(dirty_result))
    entry = next(e for e in data["entries"] if e["key"] == "DB_PASSWORD")
    assert "age_days" in entry
    assert "last_rotated" in entry
    assert entry["due"] is True
