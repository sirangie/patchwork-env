import json
import pytest
from patchwork_env.patcher import apply_patch
from patchwork_env.report_patcher import render_patch_text, render_patch_json


BASE = {"HOST": "localhost", "PORT": "5432"}


def test_text_contains_header():
    r = apply_patch(BASE, {"PORT": "9999"})
    out = render_patch_text(r)
    assert "Patch Report" in out


def test_text_shows_set_with_arrow():
    r = apply_patch(BASE, {"PORT": "9999"})
    out = render_patch_text(r)
    assert "->" in out


def test_text_shows_new_key_with_plus():
    r = apply_patch(BASE, {"NEWKEY": "val"})
    out = render_patch_text(r)
    assert "+" in out


def test_text_shows_delete_with_minus():
    r = apply_patch(BASE, {"PORT": None})
    out = render_patch_text(r)
    assert "-" in out


def test_text_shows_skip():
    r = apply_patch(BASE, {"HOST": "other"}, overwrite=False)
    out = render_patch_text(r)
    assert "skipped" in out


def test_text_empty_ops():
    r = apply_patch(BASE, {})
    out = render_patch_text(r)
    assert "No operations" in out


def test_json_structure():
    r = apply_patch(BASE, {"PORT": "9999", "HOST": None})
    data = json.loads(render_patch_json(r))
    assert "applied" in data
    assert "skipped" in data
    assert "ops" in data
    assert isinstance(data["ops"], list)


def test_json_op_fields():
    r = apply_patch(BASE, {"PORT": "1111"})
    data = json.loads(render_patch_json(r))
    op = data["ops"][0]
    assert "key" in op
    assert "action" in op
    assert "old_value" in op
    assert "new_value" in op
