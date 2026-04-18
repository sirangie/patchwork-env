"""Integration: parse -> patch -> serialize round-trip."""
import tempfile, os
from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.patcher import apply_patch


def _write(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_parse_patch_serialize():
    path = _write("HOST=localhost\nPORT=5432\nDEBUG=true\n")
    try:
        env = parse_env_file(path)
        result = apply_patch(env, {"PORT": "9999", "EXTRA": "added", "DEBUG": None})
        serialized = serialize_env(result.env)
        assert "PORT=9999" in serialized
        assert "EXTRA=added" in serialized
        assert "DEBUG" not in serialized
        assert "HOST=localhost" in serialized
    finally:
        os.unlink(path)


def test_no_overwrite_preserves_values():
    path = _write("KEY=original\n")
    try:
        env = parse_env_file(path)
        result = apply_patch(env, {"KEY": "new"}, overwrite=False)
        assert result.env["KEY"] == "original"
    finally:
        os.unlink(path)


def test_patch_empty_env():
    path = _write("")
    try:
        env = parse_env_file(path)
        result = apply_patch(env, {"A": "1", "B": "2"})
        assert result.env == {"A": "1", "B": "2"}
        assert len(result.applied) == 2
    finally:
        os.unlink(path)
