"""Compare the structure (keys only) of an env against a schema definition."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SchemaField:
    key: str
    required: bool = True
    description: str = ""
    default: Optional[str] = None


@dataclass
class SchemaDiffEntry:
    key: str
    status: str  # 'ok', 'missing_required', 'missing_optional', 'extra'
    description: str = ""
    default: Optional[str] = None

    def __repr__(self) -> str:
        return f"SchemaDiffEntry({self.key!r}, {self.status!r})"


@dataclass
class SchemaDiffResult:
    entries: List[SchemaDiffEntry] = field(default_factory=list)
    env_label: str = "env"
    schema_label: str = "schema"

    @property
    def ok(self) -> bool:
        return not any(e.status == "missing_required" for e in self.entries)

    @property
    def missing_required(self) -> List[SchemaDiffEntry]:
        return [e for e in self.entries if e.status == "missing_required"]

    @property
    def missing_optional(self) -> List[SchemaDiffEntry]:
        return [e for e in self.entries if e.status == "missing_optional"]

    @property
    def extra_keys(self) -> List[SchemaDiffEntry]:
        return [e for e in self.entries if e.status == "extra"]

    @property
    def ok_keys(self) -> List[SchemaDiffEntry]:
        return [e for e in self.entries if e.status == "ok"]


def diff_schema(
    env: Dict[str, str],
    schema: List[SchemaField],
    env_label: str = "env",
    schema_label: str = "schema",
    allow_extra: bool = True,
) -> SchemaDiffResult:
    """Diff an env dict against a list of SchemaField definitions."""
    result = SchemaDiffResult(env_label=env_label, schema_label=schema_label)
    schema_keys = {f.key for f in schema}
    schema_map = {f.key: f for f in schema}

    for f in schema:
        if f.key in env:
            result.entries.append(
                SchemaDiffEntry(f.key, "ok", f.description, f.default)
            )
        elif f.required:
            result.entries.append(
                SchemaDiffEntry(f.key, "missing_required", f.description, f.default)
            )
        else:
            result.entries.append(
                SchemaDiffEntry(f.key, "missing_optional", f.description, f.default)
            )

    if not allow_extra:
        for key in env:
            if key not in schema_keys:
                result.entries.append(SchemaDiffEntry(key, "extra"))

    return result
