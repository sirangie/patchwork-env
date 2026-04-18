import json
import pytest
from patchwork_env.exporter import export_env, SUPPORTED_FORMATS


SAMPLE = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "s3cr3t with spaces",
    "PORT": "8080",
}


def test_shell_export_contains_export_keyword():
    out = export_env(SAMPLE, "shell")
    for line in out.strip().splitlines():
        assert line.startswith("export ")


def test_shell_export_quotes_spaces():
    out = export_env(SAMPLE, "shell")
    assert "'s3cr3t with spaces'" in out or '"s3cr3t with spaces"' in out or "s3cr3t\ with\ spaces" in out


def test_shell_export_all_keys_present():
    out = export_env(SAMPLE, "shell")
    for key in SAMPLE:
        assert key in out


def test_docker_export_no_export_keyword():
    out = export_env(SAMPLE, "docker")
    for line in out.strip().splitlines():
        assert not line.startswith("export ")
        assert "=" in line


def test_docker_export_literal_value():
    out = export_env({"KEY": "val with spaces"}, "docker")
    assert "KEY=val with spaces" in out


def test_json_export_is_valid_json():
    out = export_env(SAMPLE, "json")
    parsed = json.loads(out)
    assert parsed == SAMPLE


def test_json_export_sorted_keys():
    out = export_env(SAMPLE, "json")
    parsed = json.loads(out)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE, "yaml")


def test_empty_env_all_formats():
    for fmt in SUPPORTED_FORMATS:
        out = export_env({}, fmt)
        assert isinstance(out, str)
