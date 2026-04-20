"""Tests for patchwork_env.differ_keys."""
import pytest
from patchwork_env.differ_keys import diff_keys


BASE = {"A": "1", "B": "2", "C": "3"}
TARGET = {"B": "2", "C": "99", "D": "4"}


def test_only_in_base_detected():
    r = diff_keys(BASE, TARGET)
    assert "A" in r.only_in_base


def test_only_in_target_detected():
    r = diff_keys(BASE, TARGET)
    assert "D" in r.only_in_target


def test_shared_keys_correct():
    r = diff_keys(BASE, TARGET)
    assert set(r.shared) == {"B", "C"}


def test_has_differences_true_when_mismatch():
    r = diff_keys(BASE, TARGET)
    assert r.has_differences is True


def test_has_differences_false_when_identical_keys():
    env = {"X": "1", "Y": "2"}
    r = diff_keys(env, {"X": "9", "Y": "0"})
    assert r.has_differences is False


def test_coverage_full_when_same_keys():
    env = {"X": "1", "Y": "2"}
    r = diff_keys(env, {"X": "9", "Y": "0"})
    assert r.coverage == 1.0


def test_coverage_partial():
    r = diff_keys({"A": "1", "B": "2"}, {"A": "1", "C": "3"})
    # shared=1, total_unique=3 -> 1/3
    assert abs(r.coverage - 1 / 3) < 1e-6


def test_empty_envs_coverage_is_one():
    r = diff_keys({}, {})
    assert r.coverage == 1.0


def test_labels_stored():
    r = diff_keys({}, {}, base_label="prod", target_label="staging")
    assert r.base_label == "prod"
    assert r.target_label == "staging"


def test_total_unique():
    r = diff_keys({"A": "1", "B": "2"}, {"B": "2", "C": "3"})
    assert r.total_unique == 3


def test_sorted_output():
    base = {"Z": "1", "A": "2", "M": "3"}
    target = {"A": "2"}
    r = diff_keys(base, target)
    assert r.only_in_base == sorted(r.only_in_base)
