"""Integration: parse -> rename -> serialize round-trip."""
import os
import tempfile
from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.renamer import rename_keys


def _write(tmp_dir, name, content):
    p = os.path.join(tmp_dir, name)
    with open(p, "w") as f:
        f.write(content)
    return p


def test_parse_rename_serialize():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "OLD_DB=postgres\nPORT=5432\n")
        env = parse_env_file(p)
        result = rename_keys(env, {"OLD_DB": "DATABASE_URL"})
        out = serialize_env(result.env)
        assert "DATABASE_URL=postgres" in out
        assert "OLD_DB" not in out
        assert "PORT=5432" in out


def test_conflict_does_not_corrupt_file():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "A=1\nB=2\n")
        env = parse_env_file(p)
        result = rename_keys(env, {"A": "B"})  # B already exists -> conflict
        assert result.env["A"] == "1"
        assert result.env["B"] == "2"
        assert len(result.conflicts) == 1


def test_empty_env_rename_noop():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "")
        env = parse_env_file(p)
        result = rename_keys(env, {"GHOST": "SPIRIT"})
        assert result.env == {}
        assert len(result.skipped) == 1
