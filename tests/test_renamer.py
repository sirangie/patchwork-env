import pytest
from patchwork_env.renamer import rename_keys, RenameOp


ENV = {"OLD_KEY": "hello", "KEEP": "world", "EXISTING": "there"}


def test_basic_rename():
    r = rename_keys(ENV, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in r.env
    assert "OLD_KEY" not in r.env
    assert r.env["NEW_KEY"] == "hello"


def test_renamed_op_recorded():
    r = rename_keys(ENV, {"OLD_KEY": "NEW_KEY"})
    assert len(r.renamed) == 1
    assert r.renamed[0].old_key == "OLD_KEY"
    assert r.renamed[0].new_key == "NEW_KEY"
    assert r.renamed[0].status == "renamed"


def test_missing_key_is_skipped():
    r = rename_keys(ENV, {"MISSING": "WHATEVER"})
    assert len(r.skipped) == 1
    assert r.skipped[0].old_key == "MISSING"
    assert "WHATEVER" not in r.env


def test_conflict_when_new_key_exists():
    r = rename_keys(ENV, {"OLD_KEY": "EXISTING"})
    assert len(r.conflicts) == 1
    # original keys unchanged
    assert "OLD_KEY" in r.env
    assert r.env["EXISTING"] == "there"


def test_overwrite_resolves_conflict():
    r = rename_keys(ENV, {"OLD_KEY": "EXISTING"}, overwrite=True)
    assert len(r.renamed) == 1
    assert r.env["EXISTING"] == "hello"
    assert "OLD_KEY" not in r.env


def test_unrelated_keys_preserved():
    r = rename_keys(ENV, {"OLD_KEY": "NEW_KEY"})
    assert r.env["KEEP"] == "world"


def test_multiple_renames():
    env = {"A": "1", "B": "2"}
    r = rename_keys(env, {"A": "X", "B": "Y"})
    assert r.env == {"X": "1", "Y": "2"}
    assert len(r.renamed) == 2


def test_empty_mapping_no_ops():
    r = rename_keys(ENV, {})
    assert r.env == ENV
    assert r.ops == []
