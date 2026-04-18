"""Tests for patchwork_env.templater."""

import os
import tempfile

import pytest

from patchwork_env.templater import (
    TemplateEntry,
    build_template,
    serialize_template,
    write_template,
    _is_safe_key,
)


def _tmp_env(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".env")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def test_safe_key_detection():
    assert _is_safe_key("") is True
    assert _is_safe_key("APP_ENV") is True
    assert _is_safe_key("LOG_LEVEL") is True
    assert _is_safe_key("SECRET_KEY") is False
    assert _is_safe_key("DATABASE_URL") is False


def test_build_template_masks_secrets():
    path = _tmp_env("SECRET_KEY=supersecret\nDEBUG=true\n")
    entries = build_template(path)
    by_key = {e.key: e for e in entries}
    assert by_key["SECRET_KEY"].placeholder == ""
    assert by_key["SECRET_KEY"].kept is False
    assert by_key["DEBUG"].placeholder == "true"
    assert by_key["DEBUG"].kept is True


def test_build_template_custom_placeholder():
    path = _tmp_env("API_TOKEN=abc123\n")
    entries = build_template(path, placeholder="CHANGEME")
    assert entries[0].placeholder == "CHANGEME"


def test_build_template_keep_safe_false():
    path = _tmp_env("DEBUG=true\nSECRET=x\n")
    entries = build_template(path, keep_safe=False)
    for e in entries:
        assert e.placeholder == ""
        assert e.kept is False


def test_serialize_template():
    entries = [
        TemplateEntry(key="FOO", placeholder=""),
        TemplateEntry(key="DEBUG", placeholder="true", kept=True),
    ]
    out = serialize_template(entries)
    assert "FOO=\n" in out
    assert "DEBUG=true\n" in out


def test_serialize_template_empty():
    assert serialize_template([]) == ""


def test_write_template(tmp_path):
    entries = [TemplateEntry(key="KEY", placeholder="val")]
    dest = str(tmp_path / ".env.template")
    write_template(entries, dest)
    with open(dest) as f:
        content = f.read()
    assert "KEY=val" in content
