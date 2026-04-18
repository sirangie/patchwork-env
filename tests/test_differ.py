"""Tests for patchwork_env.differ"""

import pytest
from patchwork_env.differ import diff_envs, summary, DiffEntry


LEFT = {
    'APP_NAME': 'myapp',
    'DEBUG': 'true',
    'SECRET_KEY': 'abc123',
    'OLD_VAR': 'gone',
}

RIGHT = {
    'APP_NAME': 'myapp',
    'DEBUG': 'false',
    'SECRET_KEY': 'xyz789',
    'NEW_VAR': 'here',
}


def test_unchanged_key():
    entries = diff_envs(LEFT, RIGHT)
    unchanged = [e for e in entries if e.key == 'APP_NAME']
    assert len(unchanged) == 1
    assert unchanged[0].status == 'unchanged'


def test_changed_key():
    entries = diff_envs(LEFT, RIGHT)
    changed = [e for e in entries if e.key == 'DEBUG']
    assert changed[0].status == 'changed'
    assert changed[0].left_value == 'true'
    assert changed[0].right_value == 'false'


def test_removed_key():
    entries = diff_envs(LEFT, RIGHT)
    removed = [e for e in entries if e.key == 'OLD_VAR']
    assert removed[0].status == 'removed'
    assert removed[0].right_value is None


def test_added_key():
    entries = diff_envs(LEFT, RIGHT)
    added = [e for e in entries if e.key == 'NEW_VAR']
    assert added[0].status == 'added'
    assert added[0].left_value is None


def test_mask_values():
    entries = diff_envs(LEFT, RIGHT, mask_values=True)
    for e in entries:
        if e.left_value is not None:
            assert e.left_value == '***'
        if e.right_value is not None:
            assert e.right_value == '***'


def test_summary_counts():
    entries = diff_envs(LEFT, RIGHT)
    s = summary(entries)
    assert s['unchanged'] == 1
    assert s['changed'] == 2
    assert s['removed'] == 1
    assert s['added'] == 1


def test_empty_dicts():
    entries = diff_envs({}, {})
    assert entries == []


def test_diff_entry_repr_added():
    e = DiffEntry('FOO', 'added', right_value='bar')
    assert repr(e) == '+ FOO=bar'


def test_diff_entry_repr_removed():
    e = DiffEntry('FOO', 'removed', left_value='bar')
    assert repr(e) == '- FOO=bar'
