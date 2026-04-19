import json
import pytest
from patchwork_env.grouper import group_env
from patchwork_env.report_grouper import render_group_text, render_group_json


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "SOLO": "alone",
}


@pytest.fixture
def result():
    return group_env(ENV)


def test_text_contains_header(result):
    out = render_group_text(result)
    assert "Key Groups" in out


def test_text_shows_group_names(result):
    out = render_group_text(result)
    assert "[DB]" in out
    assert "[AWS]" in out


def test_text_shows_ungrouped(result):
    out = render_group_text(result)
    assert "ungrouped" in out
    assert "SOLO" in out


def test_text_hides_values_by_default(result):
    out = render_group_text(result)
    assert "localhost" not in out


def test_text_shows_values_when_requested(result):
    out = render_group_text(result, show_values=True)
    assert "localhost" in out


def test_json_structure(result):
    raw = render_group_json(result)
    data = json.loads(raw)
    assert "groups" in data
    assert "ungrouped" in data
    assert "total_keys" in data


def test_json_group_keys_correct(result):
    data = json.loads(render_group_json(result))
    assert "DB_HOST" in data["groups"]["DB"]
    assert "DB_PORT" in data["groups"]["DB"]


def test_json_ungrouped_list(result):
    data = json.loads(render_group_json(result))
    assert "SOLO" in data["ungrouped"]
