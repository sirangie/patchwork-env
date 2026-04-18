import json
import pytest
from patchwork_env.sorter import sort_env
from patchwork_env.report_sorter import render_sort_text, render_sort_json


SAMPLE = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


def test_basic_sort_alphabetical():
    result = sort_env(SAMPLE)
    assert result.sorted_order == ["APPLE", "MANGO", "ZEBRA"]


def test_reverse_sort():
    result = sort_env(SAMPLE, reverse=True)
    assert result.sorted_order == ["ZEBRA", "MANGO", "APPLE"]


def test_sorted_env_dict_order_matches():
    result = sort_env(SAMPLE)
    assert list(result.env.keys()) == result.sorted_order


def test_original_order_preserved():
    result = sort_env(SAMPLE)
    assert result.original_order == list(SAMPLE.keys())


def test_moved_count():
    result = sort_env(SAMPLE)
    # APPLE moves from index 1->0, ZEBRA from 0->2 etc.
    assert result.moved > 0


def test_already_sorted_has_zero_moved():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_env(env)
    assert result.moved == 0


def test_group_prefixes_cluster_keys():
    env = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "p", "APP_ENV": "e", "OTHER": "o"}
    result = sort_env(env, group_prefixes=["DB_", "APP_"])
    order = result.sorted_order
    db_end = max(order.index(k) for k in ["DB_HOST", "DB_PORT"])
    app_start = min(order.index(k) for k in ["APP_NAME", "APP_ENV"])
    assert db_end < app_start, "DB_ group should come before APP_ group"


def test_group_prefixes_remainder_at_end():
    env = {"DB_HOST": "h", "ZZOTHER": "z", "DB_PORT": "p"}
    result = sort_env(env, group_prefixes=["DB_"])
    assert result.sorted_order[-1] == "ZZOTHER"


def test_render_text_contains_header():
    result = sort_env(SAMPLE)
    text = render_sort_text(result)
    assert "Sort Result" in text
    assert "APPLE" in text


def test_render_text_show_values():
    result = sort_env(SAMPLE)
    text = render_sort_text(result, show_values=True)
    assert "APPLE=2" in text


def test_render_json_structure():
    result = sort_env(SAMPLE)
    data = json.loads(render_sort_json(result))
    assert "sorted_order" in data
    assert "original_order" in data
    assert data["total"] == 3
