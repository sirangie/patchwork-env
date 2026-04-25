"""Tests for patchwork_env.caster."""
import pytest
from patchwork_env.caster import cast_env, CastResult


SAMPLE = {
    "PORT": "8080",
    "DEBUG": "true",
    "RATIO": "0.75",
    "NAME": "myapp",
    "WORKERS": "4",
    "VERBOSE": "yes",
    "ENABLED": "false",
    "BAD_INT": "notanumber",
    "BAD_BOOL": "maybe",
}

SCHEMA = {
    "PORT": "int",
    "DEBUG": "bool",
    "RATIO": "float",
    "NAME": "str",
    "WORKERS": "int",
    "VERBOSE": "bool",
    "ENABLED": "bool",
    "BAD_INT": "int",
    "BAD_BOOL": "bool",
}


@pytest.fixture
def result() -> CastResult:
    return cast_env(SAMPLE, SCHEMA)


def test_int_cast_correct(result):
    assert result.typed["PORT"] == 8080


def test_float_cast_correct(result):
    assert result.typed["RATIO"] == pytest.approx(0.75)


def test_bool_true_variants(result):
    assert result.typed["DEBUG"] is True
    assert result.typed["VERBOSE"] is True


def test_bool_false_variant(result):
    assert result.typed["ENABLED"] is False


def test_str_passthrough(result):
    assert result.typed["NAME"] == "myapp"


def test_success_count(result):
    # PORT, DEBUG, RATIO, NAME, WORKERS, VERBOSE, ENABLED = 7 ok
    assert result.success_count == 7


def test_failure_count(result):
    assert result.failure_count == 2


def test_failures_list_keys(result):
    failed_keys = {op.key for op in result.failures}
    assert "BAD_INT" in failed_keys
    assert "BAD_BOOL" in failed_keys


def test_failed_value_is_none(result):
    bad = next(o for o in result.failures if o.key == "BAD_INT")
    assert bad.value is None


def test_failed_op_has_error_message(result):
    bad = next(o for o in result.failures if o.key == "BAD_BOOL")
    assert bad.error is not None
    assert len(bad.error) > 0


def test_no_schema_defaults_to_str():
    env = {"KEY": "hello"}
    r = cast_env(env, {})
    assert r.typed["KEY"] == "hello"
    assert r.success_count == 1


def test_unknown_type_is_failure():
    r = cast_env({"X": "1"}, {"X": "uuid"})
    assert r.failure_count == 1
    assert r.failures[0].key == "X"


def test_empty_env_returns_empty_result():
    r = cast_env({}, {"PORT": "int"})
    assert r.success_count == 0
    assert r.failure_count == 0
    assert r.typed == {}
