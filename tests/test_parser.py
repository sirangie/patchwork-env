"""Tests for patchwork_env.parser"""

import textwrap
import tempfile
import os
import pytest

from patchwork_env.parser import parse_env_file, serialize_env, _clean_value


def write_tmp_env(content: str) -> str:
    """Write content to a temp file and return its path."""
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
    tf.write(textwrap.dedent(content))
    tf.close()
    return tf.name


def test_basic_key_value():
    path = write_tmp_env("""
        DB_HOST=localhost
        DB_PORT=5432
    """)
    env = parse_env_file(path)
    assert env['DB_HOST'] == 'localhost'
    assert env['DB_PORT'] == '5432'
    os.unlink(path)


def test_quoted_values():
    path = write_tmp_env("""
        SECRET="hello world"
        TOKEN='abc123'
    """)
    env = parse_env_file(path)
    assert env['SECRET'] == 'hello world'
    assert env['TOKEN'] == 'abc123'
    os.unlink(path)


def test_inline_comment_stripped():
    assert _clean_value('myvalue # this is a comment') == 'myvalue'


def test_comment_lines_skipped():
    path = write_tmp_env("""
        # this is a comment
        APP_ENV=production
    """)
    env = parse_env_file(path)
    assert list(env.keys()) == ['APP_ENV']
    os.unlink(path)


def test_blank_lines_skipped():
    path = write_tmp_env("""
        FOO=bar

        BAZ=qux
    """)
    env = parse_env_file(path)
    assert len(env) == 2
    os.unlink(path)


def test_serialize_roundtrip():
    original = {'Z_KEY': 'last', 'A_KEY': 'first', 'M_KEY': 'value with spaces'}
    serialized = serialize_env(original)
    path = write_tmp_env(serialized)
    recovered = parse_env_file(path)
    assert recovered == original
    os.unlink(path)
