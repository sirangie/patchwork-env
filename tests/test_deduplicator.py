import pytest
from patchwork_env.deduplicator import deduplicate_env, DedupeOp, DedupeResult


def _pairs(*items):
    """Helper: accepts alternating key, value strings."""
    it = iter(items)
    return list(zip(it, it))


def test_no_duplicates_returns_clean():
    result = deduplicate_env(_pairs("A", "1", "B", "2"))
    assert result.clean
    assert result.deduplicated_count == 0


def test_no_duplicates_env_intact():
    result = deduplicate_env(_pairs("A", "1", "B", "2"))
    assert result.env == {"A": "1", "B": "2"}


def test_last_wins_by_default():
    pairs = [("KEY", "first"), ("KEY", "second")]
    result = deduplicate_env(pairs)
    assert result.env["KEY"] == "second"


def test_first_wins_strategy():
    pairs = [("KEY", "first"), ("KEY", "second")]
    result = deduplicate_env(pairs, strategy="first")
    assert result.env["KEY"] == "first"


def test_op_recorded_for_duplicate():
    pairs = [("KEY", "v1"), ("KEY", "v2")]
    result = deduplicate_env(pairs)
    assert len(result.ops) == 1
    assert result.ops[0].key == "KEY"


def test_op_dropped_values_last_strategy():
    pairs = [("KEY", "v1"), ("KEY", "v2"), ("KEY", "v3")]
    result = deduplicate_env(pairs, strategy="last")
    op = result.ops[0]
    assert op.kept_value == "v3"
    assert op.dropped_values == ["v1", "v2"]


def test_op_dropped_values_first_strategy():
    pairs = [("KEY", "v1"), ("KEY", "v2"), ("KEY", "v3")]
    result = deduplicate_env(pairs, strategy="first")
    op = result.ops[0]
    assert op.kept_value == "v1"
    assert op.dropped_values == ["v2", "v3"]


def test_multiple_duplicate_keys():
    pairs = [("A", "1"), ("A", "2"), ("B", "x"), ("B", "y")]
    result = deduplicate_env(pairs)
    assert result.deduplicated_count == 2
    assert result.env["A"] == "2"
    assert result.env["B"] == "y"


def test_deduplicated_keys_list():
    pairs = [("FOO", "a"), ("FOO", "b"), ("BAR", "c")]
    result = deduplicate_env(pairs)
    assert "FOO" in result.deduplicated_keys
    assert "BAR" not in result.deduplicated_keys


def test_original_order_preserved():
    pairs = [("Z", "1"), ("A", "2"), ("M", "3")]
    result = deduplicate_env(pairs)
    assert list(result.env.keys()) == ["Z", "A", "M"]


def test_strategy_stored_in_op():
    pairs = [("X", "1"), ("X", "2")]
    result = deduplicate_env(pairs, strategy="first")
    assert result.ops[0].strategy == "first"
