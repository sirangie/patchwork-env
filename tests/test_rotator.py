"""Tests for patchwork_env.rotator."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from patchwork_env.rotator import RotateResult, check_rotation, _parse_iso


def _iso(days_ago: float) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


SECRET_ENV = {
    "SECRET_KEY": "abc",
    "API_TOKEN": "xyz",
    "DATABASE_PASSWORD": "s3cr3t",
    "APP_NAME": "myapp",          # safe — should be skipped in secret_only mode
}


def test_parse_iso_valid():
    dt = _parse_iso("2023-01-15T00:00:00+00:00")
    assert dt is not None
    assert dt.year == 2023


def test_parse_iso_invalid_returns_none():
    assert _parse_iso("not-a-date") is None
    assert _parse_iso("") is None


def test_no_timestamps_all_due():
    result = check_rotation({"SECRET_KEY": "v"}, timestamps={}, threshold_days=90)
    assert result.due_count == 1
    assert result.clean is False


def test_recent_rotation_not_due():
    ts = {"API_TOKEN": _iso(10)}
    result = check_rotation({"API_TOKEN": "v"}, timestamps=ts, threshold_days=90)
    assert result.due_count == 0
    assert result.clean is True


def test_old_rotation_is_due():
    ts = {"SECRET_KEY": _iso(100)}
    result = check_rotation({"SECRET_KEY": "v"}, timestamps=ts, threshold_days=90)
    assert result.due_count == 1
    assert "SECRET_KEY" in result.due_keys


def test_safe_key_skipped_in_secret_only_mode():
    result = check_rotation(
        {"APP_NAME": "myapp"},
        timestamps={},
        threshold_days=90,
        secret_only=True,
    )
    # APP_NAME is not a secret key
    assert len(result.entries) == 0


def test_safe_key_included_when_secret_only_false():
    result = check_rotation(
        {"APP_NAME": "myapp"},
        timestamps={},
        threshold_days=90,
        secret_only=False,
    )
    assert len(result.entries) == 1
    assert result.entries[0].key == "APP_NAME"


def test_mixed_keys_counts():
    ts = {
        "SECRET_KEY": _iso(10),
        "API_TOKEN": _iso(200),
    }
    result = check_rotation(
        {"SECRET_KEY": "a", "API_TOKEN": "b", "DATABASE_PASSWORD": "c"},
        timestamps=ts,
        threshold_days=90,
    )
    assert result.ok_count == 1
    assert result.due_count == 2   # API_TOKEN (old) + DATABASE_PASSWORD (no ts)


def test_age_days_computed():
    ts = {"SECRET_KEY": _iso(45)}
    result = check_rotation({"SECRET_KEY": "v"}, timestamps=ts, threshold_days=90)
    entry = result.entries[0]
    assert entry.age_days is not None
    assert 44 < entry.age_days < 46


def test_threshold_respected():
    ts = {"API_TOKEN": _iso(30)}
    # strict threshold: 20 days
    result = check_rotation({"API_TOKEN": "v"}, timestamps=ts, threshold_days=20)
    assert result.due_count == 1
