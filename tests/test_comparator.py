import pytest
from patchwork_env.comparator import compare_envs, CompareEntry


L = {"A": "1", "B": "2", "C": "3"}
R = {"A": "1", "B": "99", "D": "4"}


def test_same_key_detected():
    result = compare_envs({"X": "1"}, {"X": "1"})
    assert result.same[0].key == "X"


def test_changed_key_detected():
    result = compare_envs(L, R)
    changed_keys = [e.key for e in result.changed]
    assert "B" in changed_keys


def test_removed_key_detected():
    result = compare_envs(L, R)
    removed_keys = [e.key for e in result.removed]
    assert "C" in removed_keys


def test_added_key_detected():
    result = compare_envs(L, R)
    added_keys = [e.key for e in result.added]
    assert "D" in added_keys


def test_identical_envs():
    result = compare_envs({"A": "1"}, {"A": "1"})
    assert result.is_identical


def test_not_identical_when_changed():
    result = compare_envs(L, R)
    assert not result.is_identical


def test_labels_stored():
    result = compare_envs({}, {}, left_label="prod", right_label="staging")
    assert result.left_label == "prod"
    assert result.right_label == "staging"


def test_entry_left_none_for_added():
    result = compare_envs({}, {"NEW": "val"})
    e = result.entries[0]
    assert e.left is None
    assert e.right == "val"


def test_entry_right_none_for_removed():
    result = compare_envs({"OLD": "val"}, {})
    e = result.entries[0]
    assert e.right is None


def test_all_keys_present_in_entries():
    result = compare_envs(L, R)
    keys = {e.key for e in result.entries}
    assert keys == {"A", "B", "C", "D"}
