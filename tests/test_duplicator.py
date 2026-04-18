"""Tests for duplicator and report_duplicator."""
import json
import pytest
from patchwork_env.duplicator import find_duplicates, DuplicateEntry
from patchwork_env.report_duplicator import render_duplicate_text, render_duplicate_json


SIMPLE = [
    "FOO=bar\n",
    "BAZ=qux\n",
]

WITH_DUP = [
    "FOO=first\n",
    "BAR=hello\n",
    "FOO=second\n",
]

MULTI_DUP = [
    "A=1\n",
    "B=2\n",
    "A=3\n",
    "B=4\n",
    "B=5\n",
]


def test_no_duplicates_in_clean_file():
    result = find_duplicates(SIMPLE)
    assert not result.has_duplicates
    assert result.duplicate_count == 0


def test_total_keys_scanned():
    result = find_duplicates(SIMPLE)
    assert result.total_keys_scanned == 2


def test_duplicate_detected():
    result = find_duplicates(WITH_DUP)
    assert result.has_duplicates
    assert result.duplicate_count == 1
    assert result.entries[0].key == "FOO"


def test_duplicate_occurrences_count():
    result = find_duplicates(WITH_DUP)
    assert result.entries[0].occurrences == 2


def test_duplicate_values_captured():
    result = find_duplicates(WITH_DUP)
    assert "first" in result.entries[0].values
    assert "second" in result.entries[0].values


def test_multiple_duplicate_keys():
    result = find_duplicates(MULTI_DUP)
    keys = {e.key for e in result.entries}
    assert keys == {"A", "B"}


def test_comments_and_blanks_ignored():
    lines = ["# comment\n", "\n", "KEY=val\n", "KEY=val2\n"]
    result = find_duplicates(lines)
    assert result.duplicate_count == 1
    assert result.total_keys_scanned == 2


def test_render_text_no_duplicates():
    result = find_duplicates(SIMPLE)
    text = render_duplicate_text(result)
    assert "No duplicate" in text


def test_render_text_shows_dup_key():
    result = find_duplicates(WITH_DUP)
    text = render_duplicate_text(result)
    assert "FOO" in text
    assert "DUP" in text


def test_render_json_structure():
    result = find_duplicates(WITH_DUP)
    data = json.loads(render_duplicate_json(result))
    assert "duplicates" in data
    assert data["duplicate_count"] == 1
    assert data["duplicates"][0]["key"] == "FOO"
