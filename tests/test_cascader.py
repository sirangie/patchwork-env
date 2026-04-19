import pytest
from patchwork_env.cascader import cascade_envs, CascadeResult


def _layers(*pairs):
    """Helper: list of (label, dict) tuples."""
    return list(pairs)


def test_single_layer_all_keys_present():
    result = cascade_envs([("base", {"A": "1", "B": "2"})])
    assert result.env == {"A": "1", "B": "2"}


def test_later_layer_overrides_earlier():
    result = cascade_envs([
        ("base", {"A": "1"}),
        ("prod", {"A": "99"}),
    ])
    assert result.env["A"] == "99"


def test_source_tracks_winning_layer():
    result = cascade_envs([
        ("base", {"A": "1"}),
        ("prod", {"A": "99"}),
    ])
    assert result.source_for("A") == "prod"


def test_non_overlapping_keys_all_present():
    result = cascade_envs([
        ("base", {"A": "1"}),
        ("prod", {"B": "2"}),
    ])
    assert "A" in result.env
    assert "B" in result.env


def test_overridden_keys_listed():
    result = cascade_envs([
        ("base", {"A": "1", "B": "x"}),
        ("prod", {"A": "2"}),
    ])
    assert "A" in result.overridden_keys
    assert "B" not in result.overridden_keys


def test_layer_labels_stored():
    result = cascade_envs([
        ("base", {}),
        ("staging", {}),
        ("prod", {}),
    ])
    assert result.layer_labels == ["base", "staging", "prod"]


def test_total_keys_count():
    result = cascade_envs([
        ("base", {"A": "1", "B": "2"}),
        ("prod", {"C": "3"}),
    ])
    assert result.total_keys == 3


def test_three_layer_cascade_last_wins():
    result = cascade_envs([
        ("base", {"X": "base"}),
        ("staging", {"X": "staging"}),
        ("prod", {"X": "prod"}),
    ])
    assert result.env["X"] == "prod"
    assert result.source_for("X") == "prod"


def test_empty_layers_returns_empty():
    result = cascade_envs([])
    assert result.env == {}
    assert result.total_keys == 0


def test_source_for_missing_key_returns_none():
    result = cascade_envs([("base", {"A": "1"})])
    assert result.source_for("MISSING") is None
