import pytest
from patchwork_env.freezer import freeze_env, check_frozen, FreezeViolation


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_freeze_returns_copy():
    frozen = freeze_env(BASE)
    assert frozen == BASE
    assert frozen is not BASE


def test_no_violations_when_identical():
    frozen = freeze_env(BASE)
    result = check_frozen(frozen, dict(BASE))
    assert result.ok
    assert result.violation_count == 0


def test_changed_value_is_violation():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["PORT"] = "9999"
    result = check_frozen(frozen, current)
    assert not result.ok
    assert "PORT" in result.violated_keys


def test_removed_key_is_violation():
    frozen = freeze_env(BASE)
    current = {k: v for k, v in BASE.items() if k != "DEBUG"}
    result = check_frozen(frozen, current)
    assert not result.ok
    v = next(x for x in result.violations if x.key == "DEBUG")
    assert v.actual is None


def test_added_key_not_violation_by_default():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["NEW_KEY"] = "surprise"
    result = check_frozen(frozen, current)
    assert result.ok


def test_added_key_is_violation_in_strict_mode():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["NEW_KEY"] = "surprise"
    result = check_frozen(frozen, current, strict=True)
    assert not result.ok
    assert "NEW_KEY" in result.violated_keys


def test_multiple_violations_all_reported():
    frozen = freeze_env(BASE)
    current = {"HOST": "remotehost", "PORT": "3306"}  # DEBUG removed, two changed
    result = check_frozen(frozen, current)
    assert result.violation_count == 3


def test_violated_keys_list():
    frozen = freeze_env(BASE)
    current = dict(BASE)
    current["HOST"] = "changed"
    result = check_frozen(frozen, current)
    assert result.violated_keys == ["HOST"]
