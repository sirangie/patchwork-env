"""Tests for differ_schema module."""
import pytest
from patchwork_env.differ_schema import SchemaField, diff_schema


def _schema(*fields):
    return list(fields)


def test_all_required_present_is_ok():
    env = {"HOST": "localhost", "PORT": "5432"}
    schema = _schema(
        SchemaField("HOST", required=True),
        SchemaField("PORT", required=True),
    )
    result = diff_schema(env, schema)
    assert result.ok is True


def test_missing_required_key_not_ok():
    env = {"HOST": "localhost"}
    schema = _schema(
        SchemaField("HOST", required=True),
        SchemaField("PORT", required=True),
    )
    result = diff_schema(env, schema)
    assert result.ok is False
    assert len(result.missing_required) == 1
    assert result.missing_required[0].key == "PORT"


def test_missing_optional_key_does_not_fail():
    env = {"HOST": "localhost"}
    schema = _schema(
        SchemaField("HOST", required=True),
        SchemaField("DEBUG", required=False),
    )
    result = diff_schema(env, schema)
    assert result.ok is True
    assert len(result.missing_optional) == 1
    assert result.missing_optional[0].key == "DEBUG"


def test_extra_keys_allowed_by_default():
    env = {"HOST": "localhost", "EXTRA": "value"}
    schema = _schema(SchemaField("HOST", required=True))
    result = diff_schema(env, schema)
    assert len(result.extra_keys) == 0


def test_extra_keys_flagged_when_disallowed():
    env = {"HOST": "localhost", "EXTRA": "value"}
    schema = _schema(SchemaField("HOST", required=True))
    result = diff_schema(env, schema, allow_extra=False)
    assert len(result.extra_keys) == 1
    assert result.extra_keys[0].key == "EXTRA"


def test_ok_keys_counted_correctly():
    env = {"A": "1", "B": "2", "C": "3"}
    schema = _schema(
        SchemaField("A"), SchemaField("B"), SchemaField("C"), SchemaField("D")
    )
    result = diff_schema(env, schema)
    assert len(result.ok_keys) == 3


def test_description_stored_on_entry():
    env = {}
    schema = _schema(SchemaField("DB_HOST", required=True, description="Database host"))
    result = diff_schema(env, schema)
    assert result.entries[0].description == "Database host"


def test_default_stored_on_missing_entry():
    env = {}
    schema = _schema(SchemaField("TIMEOUT", required=False, default="30"))
    result = diff_schema(env, schema)
    assert result.entries[0].default == "30"


def test_env_label_and_schema_label_stored():
    result = diff_schema({}, [], env_label="prod", schema_label="spec")
    assert result.env_label == "prod"
    assert result.schema_label == "spec"


def test_empty_env_and_empty_schema_is_ok():
    result = diff_schema({}, [])
    assert result.ok is True
    assert result.entries == []
