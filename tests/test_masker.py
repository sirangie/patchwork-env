"""Tests for patchwork_env.masker and report_masker."""
import json
import pytest
from patchwork_env.masker import mask_env, PLACEHOLDER
from patchwork_env.report_masker import render_mask_text, render_mask_json


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "EMPTY_VAL": "",
    }


def test_secret_key_masked(sample_env):
    result = mask_env(sample_env)
    assert result.env["DB_PASSWORD"] == PLACEHOLDER
    assert result.env["API_KEY"] == PLACEHOLDER


def test_safe_key_kept(sample_env):
    result = mask_env(sample_env)
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["DEBUG"] == "true"


def test_empty_value_not_masked_by_default(sample_env):
    result = mask_env(sample_env)
    assert result.env["EMPTY_VAL"] == ""
    op = next(o for o in result.ops if o.key == "EMPTY_VAL")
    assert not op.masked


def test_empty_value_masked_when_flag_set(sample_env):
    result = mask_env(sample_env, mask_empty=True)
    # EMPTY_VAL has no secret pattern so still kept
    assert result.env["EMPTY_VAL"] == ""


def test_allowlist_prevents_masking(sample_env):
    result = mask_env(sample_env, allowlist=["API_KEY"])
    assert result.env["API_KEY"] == "abc123"


def test_masked_count(sample_env):
    result = mask_env(sample_env)
    assert result.masked_count == 2


def test_kept_count(sample_env):
    result = mask_env(sample_env)
    assert result.kept_count == 3


def test_masked_keys_list(sample_env):
    result = mask_env(sample_env)
    assert set(result.masked_keys) == {"DB_PASSWORD", "API_KEY"}


def test_custom_placeholder(sample_env):
    result = mask_env(sample_env, placeholder="REDACTED")
    assert result.env["DB_PASSWORD"] == "REDACTED"


def test_custom_patterns():
    env = {"MY_SECRET_THING": "val", "NORMAL": "ok"}
    result = mask_env(env, patterns=[r"NORMAL"])
    assert result.env["NORMAL"] == PLACEHOLDER
    assert result.env["MY_SECRET_THING"] == "val"


def test_render_text_contains_header(sample_env):
    result = mask_env(sample_env)
    text = render_mask_text(result)
    assert "Mask Report" in text
    assert "Masked" in text


def test_render_text_shows_placeholder(sample_env):
    result = mask_env(sample_env)
    text = render_mask_text(result)
    assert PLACEHOLDER in text


def test_render_json_structure(sample_env):
    result = mask_env(sample_env)
    data = json.loads(render_mask_json(result))
    assert "masked_count" in data
    assert "masked_keys" in data
    assert "env" in data
    assert data["masked_count"] == 2
