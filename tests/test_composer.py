"""Unit tests for patchwork_env.composer."""
import pytest

from patchwork_env.composer import compose_envs, ComposeEntry, ComposeResult


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.db", "SECRET": "s3cr3t"}


def test_last_wins_override():
    result = compose_envs([("a", A), ("b", B)], strategy="last")
    assert result.env["HOST"] == "prod.db"


def test_last_wins_source_recorded():
    result = compose_envs([("a", A), ("b", B)], strategy="last")
    assert result.source_for("HOST") == "b"


def test_first_wins_keeps_first():
    result = compose_envs([("a", A), ("b", B)], strategy="first")
    assert result.env["HOST"] == "localhost"


def test_first_wins_source_recorded():
    result = compose_envs([("a", A), ("b", B)], strategy="first")
    assert result.source_for("HOST") == "a"


def test_non_overlapping_keys_all_present():
    result = compose_envs([("a", A), ("b", B)])
    for key in list(A) + list(B):
        assert key in result.env


def test_total_keys_correct():
    result = compose_envs([("a", A), ("b", B)])
    # HOST overlaps, so 3 + 2 - 1 = 4 unique keys
    assert result.total_keys == 4


def test_keys_from_returns_correct_source():
    result = compose_envs([("a", A), ("b", B)], strategy="last")
    keys_b = result.keys_from("b")
    assert "HOST" in keys_b
    assert "SECRET" in keys_b


def test_source_labels_stored():
    result = compose_envs([("base", A), ("override", B)])
    assert result.source_labels == ["base", "override"]


def test_empty_sources_returns_empty():
    result = compose_envs([])
    assert result.total_keys == 0
    assert result.env == {}


def test_single_source():
    result = compose_envs([("only", A)])
    assert result.env == A
    for entry in result.entries:
        assert entry.source == "only"


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        compose_envs([("a", A)], strategy="random")


def test_source_for_missing_key_returns_none():
    result = compose_envs([("a", A)])
    assert result.source_for("NONEXISTENT") is None
