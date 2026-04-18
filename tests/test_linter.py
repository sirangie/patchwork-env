"""Tests for patchwork_env.linter and report_linter."""
import json
import pytest
from patchwork_env.linter import lint_env
from patchwork_env.report_linter import render_lint_text, render_lint_json


def test_clean_file_no_issues():
    src = "KEY=value\nDB_HOST=localhost\n"
    result = lint_env(src)
    assert result.ok
    assert result.issues == []


def test_spaces_around_equals_is_error():
    src = "KEY = value\n"
    result = lint_env(src)
    codes = [i.code for i in result.issues]
    assert "E001" in codes
    assert not result.ok


def test_bare_key_no_equals_is_error():
    src = "JUSTAKEYWORD\n"
    result = lint_env(src)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_duplicate_key_is_warning():
    src = "FOO=bar\nFOO=baz\n"
    result = lint_env(src)
    codes = [i.code for i in result.issues]
    assert "W001" in codes
    assert result.ok  # only a warning, no error


def test_empty_value_is_warning():
    src = "FOO=\n"
    result = lint_env(src)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_comments_skipped():
    src = "# this is a comment\nKEY=val\n"
    result = lint_env(src)
    assert result.ok
    assert not result.issues


def test_blank_lines_skipped():
    src = "\n\nKEY=val\n\n"
    result = lint_env(src)
    assert result.ok


def test_issues_sorted_by_line():
    src = "FOO=\nBAR = bad\n"
    result = lint_env(src)
    lines = [i.line for i in result.issues]
    assert lines == sorted(lines)


def test_render_text_ok():
    src = "KEY=value\n"
    out = render_lint_text(lint_env(src))
    assert "No lint errors" in out


def test_render_text_with_errors():
    src = "KEY = value\n"
    out = render_lint_text(lint_env(src))
    assert "E001" in out
    assert "error" in out.lower()


def test_render_json_structure():
    src = "FOO=\nBAR = x\n"
    data = json.loads(render_lint_json(lint_env(src)))
    assert "ok" in data
    assert "issues" in data
    assert isinstance(data["issues"], list)
    assert data["error_count"] >= 1


def test_render_json_ok_flag():
    src = "KEY=value\n"
    data = json.loads(render_lint_json(lint_env(src)))
    assert data["ok"] is True
    assert data["issues"] == []
