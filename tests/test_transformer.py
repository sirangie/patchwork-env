import pytest
from patchwork_env.transformer import transform_env, TransformResult


ENV = {
    "APP_NAME": "  MyApp  ",
    "DB_HOST": "LOCALHOST",
    "SECRET_KEY": "AbCdEf",
    "EMPTY_VAL": "",
}


def test_strip_removes_whitespace():
    r = transform_env(ENV, ["strip"])
    assert r.env["APP_NAME"] == "MyApp"


def test_lowercase_transform():
    r = transform_env(ENV, ["lowercase"])
    assert r.env["DB_HOST"] == "localhost"


def test_uppercase_transform():
    r = transform_env(ENV, ["uppercase"])
    assert r.env["SECRET_KEY"] == "ABCDEF"


def test_chained_transforms_applied_in_order():
    r = transform_env({"K": "  Hello  "}, ["strip", "uppercase"])
    assert r.env["K"] == "HELLO"


def test_changed_count_accurate():
    r = transform_env(ENV, ["strip"])
    changed_keys = {op.key for op in r.ops if op.changed}
    assert "APP_NAME" in changed_keys
    assert "EMPTY_VAL" not in changed_keys


def test_unchanged_count_accurate():
    r = transform_env({"A": "hello", "B": "world"}, ["lowercase"])
    assert r.unchanged_count == 2


def test_keys_filter_limits_scope():
    r = transform_env(ENV, ["lowercase"], keys=["DB_HOST"])
    assert r.env["DB_HOST"] == "localhost"
    assert r.env["SECRET_KEY"] == "AbCdEf"  # untouched


def test_unknown_transform_raises():
    with pytest.raises(ValueError, match="Unknown transforms"):
        transform_env(ENV, ["explode"])


def test_op_label_contains_transform_name():
    r = transform_env({"X": "hello"}, ["uppercase"])
    assert r.ops[0].transform == "uppercase"


def test_chained_label_joined_with_plus():
    r = transform_env({"X": "  hi  "}, ["strip", "uppercase"])
    assert r.ops[0].transform == "strip+uppercase"


def test_strip_quotes():
    r = transform_env({"K": "'quoted'"}, ["strip_quotes"])
    assert r.env["K"] == "quoted"


def test_empty_env_no_ops():
    r = transform_env({}, ["strip"])
    assert r.ops == []
    assert r.env == {}
