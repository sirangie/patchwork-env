import pytest
from patchwork_env.differ_multi import diff_multi, MultiDiffResult

BASE = {"A": "1", "B": "2", "C": "3"}
DEV = {"A": "1", "B": "99", "D": "4"}
PROD = {"A": "1", "B": "2", "C": "3"}


def test_labels_match_targets():
    r = diff_multi(BASE, {"dev": DEV, "prod": PROD})
    assert set(r.labels()) == {"dev", "prod"}


def test_base_label_stored():
    r = diff_multi(BASE, {"dev": DEV}, base_label="local")
    assert r.base_label == "local"


def test_changed_detected():
    r = diff_multi(BASE, {"dev": DEV})
    changed = r.changed_in("dev")
    keys = [e.key for e in changed]
    assert "B" in keys


def test_removed_detected():
    r = diff_multi(BASE, {"dev": DEV})
    changed = r.changed_in("dev")
    keys = [e.key for e in changed]
    assert "C" in keys


def test_added_detected():
    r = diff_multi(BASE, {"dev": DEV})
    changed = r.changed_in("dev")
    keys = [e.key for e in changed]
    assert "D" in keys


def test_identical_env_no_changes():
    r = diff_multi(BASE, {"prod": PROD})
    assert r.changed_in("prod") == []


def test_summary_counts():
    r = diff_multi(BASE, {"dev": DEV})
    s = r.summary()
    assert "dev" in s
    assert s["dev"].get("changed", 0) >= 1


def test_all_keys_union():
    r = diff_multi(BASE, {"dev": DEV})
    keys = r.all_keys()
    assert "A" in keys and "D" in keys


def test_mask_hides_values():
    base = {"SECRET_KEY": "abc"}
    target = {"SECRET_KEY": "xyz"}
    r = diff_multi(base, {"prod": target}, mask=True)
    entries = r.for_env("prod")
    for e in entries:
        if e.key == "SECRET_KEY":
            assert e.old_value == "***" or e.new_value == "***"
