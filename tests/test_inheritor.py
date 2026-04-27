"""Tests for patchwork_env.inheritor."""
import pytest
from patchwork_env.inheritor import inherit_env


PARENT = {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"}
CHILD = {"DB_HOST": "local-db", "APP_NAME": "myapp"}


def test_child_key_preserved_without_overwrite():
    result = inherit_env(PARENT, CHILD, overwrite=False)
    assert result.env["DB_HOST"] == "local-db"


def test_parent_key_inherited_when_missing_in_child():
    result = inherit_env(PARENT, CHILD)
    assert result.env["DB_PORT"] == "5432"
    assert result.env["SECRET"] == "s3cr3t"


def test_child_only_key_preserved():
    result = inherit_env(PARENT, CHILD)
    assert result.env["APP_NAME"] == "myapp"


def test_overwrite_replaces_child_value():
    result = inherit_env(PARENT, CHILD, overwrite=True)
    assert result.env["DB_HOST"] == "prod-db"


def test_inherited_count_correct():
    result = inherit_env(PARENT, CHILD)
    # DB_PORT and SECRET are inherited from parent
    assert result.inherited_count == 2


def test_child_only_count_correct():
    result = inherit_env(PARENT, CHILD)
    # DB_HOST (child wins) and APP_NAME
    assert result.child_only_count == 2


def test_overwritten_count_when_overwrite_false():
    result = inherit_env(PARENT, CHILD, overwrite=False)
    assert result.overwritten_count == 0


def test_overwritten_count_when_overwrite_true():
    result = inherit_env(PARENT, CHILD, overwrite=True)
    assert result.overwritten_count == 1  # DB_HOST


def test_skip_empty_parent_removes_blank_keys():
    parent = {"EMPTY_KEY": "", "REAL_KEY": "val"}
    child: dict = {}
    result = inherit_env(parent, child, skip_empty_parent=True)
    assert "EMPTY_KEY" not in result.env
    assert result.env["REAL_KEY"] == "val"


def test_skip_empty_parent_false_includes_blank_keys():
    parent = {"EMPTY_KEY": ""}
    child: dict = {}
    result = inherit_env(parent, child, skip_empty_parent=False)
    assert "EMPTY_KEY" in result.env


def test_inherited_keys_list():
    result = inherit_env(PARENT, CHILD)
    assert "DB_PORT" in result.inherited_keys()
    assert "SECRET" in result.inherited_keys()


def test_overwritten_keys_list():
    result = inherit_env(PARENT, CHILD, overwrite=True)
    assert "DB_HOST" in result.overwritten_keys()


def test_empty_parent_returns_child_only():
    result = inherit_env({}, CHILD)
    assert result.env == CHILD
    assert result.inherited_count == 0


def test_empty_child_returns_parent_keys():
    result = inherit_env(PARENT, {})
    assert result.env == PARENT
    assert result.child_only_count == 0
