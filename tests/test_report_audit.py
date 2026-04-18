"""Tests for render_audit_text in report.py."""
import pytest
from patchwork_env.report import render_audit_text


def _diff_event(changes=None, source="a.env", target="b.env"):
    return {
        "event": "diff",
        "timestamp": "2024-01-01T00:00:00+00:00",
        "source": source,
        "target": target,
        "changes": changes or [],
    }


def _sync_event(applied=None, skipped=None, target="b.env"):
    return {
        "event": "sync",
        "timestamp": "2024-01-02T00:00:00+00:00",
        "target": target,
        "applied": applied or [],
        "skipped": skipped or [],
    }


def test_empty_events():
    assert render_audit_text([]) == "No audit events recorded."


def test_diff_event_rendered():
    ev = _diff_event(changes=[{"key": "FOO", "status": "added"}])
    out = render_audit_text([ev])
    assert "diff" in out
    assert "a.env" in out
    assert "b.env" in out
    assert "1 changes" in out


def test_sync_event_rendered():
    ev = _sync_event(applied=["FOO", "BAR"], skipped=["SECRET"])
    out = render_audit_text([ev])
    assert "sync" in out
    assert "applied=2" in out
    assert "skipped=1" in out


def test_multiple_events_rendered():
    events = [_diff_event(), _sync_event()]
    out = render_audit_text(events)
    lines = out.strip().splitlines()
    assert len(lines) == 2
    assert "diff" in lines[0]
    assert "sync" in lines[1]


def test_timestamp_in_output():
    ev = _diff_event()
    out = render_audit_text([ev])
    assert "2024-01-01" in out
