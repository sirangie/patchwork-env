import pytest
from patchwork_env.merger import merge_envs, MergeResult


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.db", "PORT": "5432", "SECRET": "abc"}
C = {"HOST": "staging.db", "EXTRA": "1"}


def test_last_wins_override():
    result = merge_envs([("a", A), ("b", B)])
    assert result.merged["HOST"] == "prod.db"
    assert result.sources["HOST"] == "b"


def test_first_wins_keeps_first():
    result = merge_envs([("a", A), ("b", B)], strategy="first-wins")
    assert result.merged["HOST"] == "localhost"
    assert result.sources["HOST"] == "a"


def test_non_overlapping_keys_all_present():
    result = merge_envs([("a", A), ("b", B)])
    assert "DEBUG" in result.merged
    assert "SECRET" in result.merged


def test_no_conflicts_when_same_value():
    result = merge_envs([("a", A), ("b", B)])
    # PORT is same in both — no conflict
    conflict_keys = [k for k, _ in result.conflicts]
    assert "PORT" not in conflict_keys


def test_conflict_detected_for_different_values():
    result = merge_envs([("a", A), ("b", B)])
    conflict_keys = [k for k, _ in result.conflicts]
    assert "HOST" in conflict_keys


def test_three_way_merge_last_wins():
    result = merge_envs([("a", A), ("b", B), ("c", C)])
    assert result.merged["HOST"] == "staging.db"
    assert result.merged["EXTRA"] == "1"


def test_has_conflicts_property():
    result = merge_envs([("a", A), ("b", B)])
    assert result.has_conflicts is True


def test_no_conflicts_identical_envs():
    result = merge_envs([("x", A), ("y", A)])
    assert result.has_conflicts is False


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([("a", A)], strategy="random")


def test_single_env_no_conflicts():
    result = merge_envs([("only", A)])
    assert result.merged == A
    assert result.has_conflicts is False
