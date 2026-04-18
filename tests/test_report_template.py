"""Tests for patchwork_env.report_template."""

import json

from patchwork_env.templater import TemplateEntry
from patchwork_env.report_template import render_template_text, render_template_json


def _entries():
    return [
        TemplateEntry(key="DEBUG", placeholder="true", kept=True),
        TemplateEntry(key="SECRET_KEY", placeholder="", kept=False),
        TemplateEntry(key="DB_URL", placeholder="", kept=False),
    ]


def test_render_text_contains_summary():
    out = render_template_text(_entries())
    assert "Template generation summary" in out
    assert "Kept (1)" in out
    assert "Masked (2)" in out


def test_render_text_kept_shows_value():
    out = render_template_text(_entries())
    assert "DEBUG=true" in out


def test_render_text_masked_shows_blank():
    out = render_template_text(_entries())
    assert "SECRET_KEY=" in out


def test_render_text_totals():
    out = render_template_text(_entries())
    assert "Total: 3 keys" in out
    assert "kept: 1" in out
    assert "masked: 2" in out


def test_render_json_structure():
    out = render_template_json(_entries())
    data = json.loads(out)
    assert data["total"] == 3
    assert len(data["entries"]) == 3
    first = data["entries"][0]
    assert "key" in first
    assert "placeholder" in first
    assert "kept" in first


def test_render_json_kept_flag():
    out = render_template_json(_entries())
    data = json.loads(out)
    by_key = {e["key"]: e for e in data["entries"]}
    assert by_key["DEBUG"]["kept"] is True
    assert by_key["SECRET_KEY"]["kept"] is False
