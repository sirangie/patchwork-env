import pytest
from patchwork_env.patcher import apply_patch, patch_summary


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_set_new_key():
    r = apply_patch(BASE, {"NEW_KEY": "hello"})
    assert r.env["NEW_KEY"] == "hello"
    assert any(o.action == "set" and o.key == "NEW_KEY" for o in r.ops)


def test_overwrite_existing_key():
    r = apply_patch(BASE, {"PORT": "9999"})
    assert r.env["PORT"] == "9999"
    op = next(o for o in r.ops if o.key == "PORT")
    assert op.action == "set"
    assert op.old_value == "5432"


def test_skip_existing_when_no_overwrite():
    r = apply_patch(BASE, {"PORT": "9999"}, overwrite=False)
    assert r.env["PORT"] == "5432"
    op = next(o for o in r.ops if o.key == "PORT")
    assert op.action == "skip"


def test_delete_existing_key():
    r = apply_patch(BASE, {"DEBUG": None})
    assert "DEBUG" not in r.env
    op = next(o for o in r.ops if o.key == "DEBUG")
    assert op.action == "delete"


def test_delete_missing_key_is_skip():
    r = apply_patch(BASE, {"MISSING": None})
    op = next(o for o in r.ops if o.key == "MISSING")
    assert op.action == "skip"


def test_delete_none_false_treats_none_as_set():
    r = apply_patch(BASE, {"DEBUG": None}, delete_none=False)
    assert r.env["DEBUG"] is None


def test_base_not_mutated():
    original = dict(BASE)
    apply_patch(BASE, {"HOST": "changed", "EXTRA": "x"})
    assert BASE == original


def test_applied_and_skipped_counts():
    r = apply_patch(BASE, {"HOST": "new", "PORT": "old"}, overwrite=False)
    # HOST overwritten (overwrite=False but HOST exists -> skip), PORT skip
    assert len(r.skipped) == 2
    assert len(r.applied) == 0


def test_patch_summary_string():
    r = apply_patch(BASE, {"HOST": "x", "DEBUG": None, "NEW": "y"})
    s = patch_summary(r)
    assert "set" in s
    assert "deleted" in s


def test_empty_patch():
    r = apply_patch(BASE, {})
    assert r.env == BASE
    assert r.ops == []
