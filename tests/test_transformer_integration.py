"""Integration: parse a real .env file, transform it, serialize back."""
import tempfile, os
from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.transformer import transform_env


def _write(tmp_dir, name, content):
    p = os.path.join(tmp_dir, name)
    with open(p, "w") as f:
        f.write(content)
    return p


def test_parse_transform_serialize_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "HOST=  localhost  \nPORT=8080\n")
        env = parse_env_file(p)
        result = transform_env(env, ["strip"])
        out = serialize_env(result.env)
        assert "HOST=localhost" in out
        assert "PORT=8080" in out


def test_transform_does_not_affect_unrelated_keys():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "SECRET=MyPass\nDEBUG=true\n")
        env = parse_env_file(p)
        result = transform_env(env, ["lowercase"], keys=["DEBUG"])
        assert result.env["SECRET"] == "MyPass"
        assert result.env["DEBUG"] == "true"


def test_empty_file_transform_noop():
    with tempfile.TemporaryDirectory() as d:
        p = _write(d, ".env", "")
        env = parse_env_file(p)
        result = transform_env(env, ["uppercase"])
        assert result.env == {}
        assert result.ops == []
