import json
from patchwork_env.transformer import transform_env
from patchwork_env.report_transformer import render_transform_text, render_transform_json


ENV = {"HOST": "  localhost  ", "PORT": "8080", "NAME": "myapp"}


def _result():
    return transform_env(ENV, ["strip"])


def test_text_contains_header():
    out = render_transform_text(_result())
    assert "Transform Report" in out


def test_text_shows_changed_count():
    out = render_transform_text(_result())
    assert "Changed" in out


def test_text_shows_tilde_for_changed_key():
    out = render_transform_text(_result())
    assert "~ HOST" in out


def test_text_shows_equals_for_unchanged_key():
    out = render_transform_text(_result())
    assert "= PORT" in out or "= NAME" in out


def test_text_show_values_flag():
    out = render_transform_text(_result(), show_values=True)
    assert "->" in out


def test_json_structure_keys():
    data = json.loads(render_transform_json(_result()))
    assert "changed_count" in data
    assert "unchanged_count" in data
    assert "ops" in data


def test_json_ops_have_required_fields():
    data = json.loads(render_transform_json(_result()))
    for op in data["ops"]:
        assert "key" in op
        assert "changed" in op
        assert "original" in op
        assert "result" in op


def test_json_changed_count_matches():
    r = _result()
    data = json.loads(render_transform_json(r))
    assert data["changed_count"] == r.changed_count
