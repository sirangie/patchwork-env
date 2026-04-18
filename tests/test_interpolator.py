import pytest
from patchwork_env.interpolator import interpolate_env, InterpolateResult


def test_no_references_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate_env(env)
    assert result.resolved == env
    assert result.ok


def test_simple_brace_reference():
    env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "http://localhost/api"
    assert result.ok


def test_bare_dollar_reference():
    env = {"NAME": "world", "MSG": "hello $NAME"}
    result = interpolate_env(env)
    assert result.resolved["MSG"] == "hello world"


def test_chained_references():
    env = {"A": "foo", "B": "${A}_bar", "C": "${B}_baz"}
    result = interpolate_env(env)
    assert result.resolved["C"] == "foo_bar_baz"
    assert result.ok


def test_missing_reference_marks_unresolved():
    env = {"URL": "${MISSING}/path"}
    result = interpolate_env(env)
    assert "URL" in result.unresolved
    assert not result.ok
    # value kept as-is
    assert "${MISSING}" in result.resolved["URL"]


def test_self_reference_detected_as_cycle():
    env = {"A": "${A}"}
    result = interpolate_env(env)
    assert "A" in result.cycles
    assert not result.ok


def test_mutual_cycle_detected():
    env = {"X": "${Y}", "Y": "${X}"}
    result = interpolate_env(env)
    # at least one of them flagged
    flagged = set(result.cycles)
    assert flagged & {"X", "Y"}


def test_multiple_refs_in_value():
    env = {"PROTO": "https", "HOST": "example.com", "URL": "${PROTO}://${HOST}"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "https://example.com"
    assert result.ok


def test_empty_env():
    result = interpolate_env({})
    assert result.resolved == {}
    assert result.ok


def test_result_ok_false_when_unresolved():
    result = InterpolateResult(resolved={}, unresolved=["X"])
    assert not result.ok


def test_result_ok_false_when_cycles():
    result = InterpolateResult(resolved={}, cycles=["Y"])
    assert not result.ok
