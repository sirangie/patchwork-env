import pytest
from patchwork_env.redactor import redact_env, _is_secret_key, DEFAULT_MASK


def test_secret_key_detected():
    assert _is_secret_key("DB_PASSWORD") is True
    assert _is_secret_key("API_KEY") is True
    assert _is_secret_key("AUTH_TOKEN") is True


def test_safe_key_not_detected():
    assert _is_secret_key("APP_NAME") is False
    assert _is_secret_key("PORT") is False
    assert _is_secret_key("DEBUG") is False


def test_secret_value_masked():
    env = {"DB_PASSWORD": "supersecret", "APP_NAME": "myapp"}
    result = redact_env(env)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert result.redacted["APP_NAME"] == "myapp"


def test_redacted_keys_list():
    env = {"SECRET_KEY": "abc", "TOKEN": "xyz", "HOST": "localhost"}
    result = redact_env(env)
    assert "SECRET_KEY" in result.redacted_keys
    assert "TOKEN" in result.redacted_keys
    assert "HOST" not in result.redacted_keys


def test_count_matches_redacted_keys():
    env = {"PASSWORD": "pass", "USER": "admin", "API_KEY": "key"}
    result = redact_env(env)
    assert result.count == len(result.redacted_keys)


def test_custom_mask():
    env = {"TOKEN": "secret"}
    result = redact_env(env, mask="<hidden>")
    assert result.redacted["TOKEN"] == "<hidden>"


def test_extra_keys_redacted():
    env = {"MY_VAR": "value", "OTHER": "data"}
    result = redact_env(env, extra_keys=["MY_VAR"])
    assert result.redacted["MY_VAR"] == DEFAULT_MASK
    assert result.redacted["OTHER"] == "data"


def test_original_unchanged():
    env = {"TOKEN": "real_value"}
    result = redact_env(env)
    assert result.original["TOKEN"] == "real_value"


def test_empty_env():
    result = redact_env({})
    assert result.count == 0
    assert result.redacted == {}
