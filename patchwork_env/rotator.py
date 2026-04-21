"""rotator.py — track which keys are due for rotation based on age."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class RotateEntry:
    key: str
    last_rotated: Optional[str]   # ISO-8601 or None if unknown
    age_days: Optional[float]     # None if no timestamp available
    due: bool                     # True when rotation is needed
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"RotateEntry({self.key!r}, due={self.due}, reason={self.reason!r})"


@dataclass
class RotateResult:
    entries: List[RotateEntry] = field(default_factory=list)
    threshold_days: int = 90

    @property
    def due_count(self) -> int:
        return sum(1 for e in self.entries if e.due)

    @property
    def ok_count(self) -> int:
        return len(self.entries) - self.due_count

    @property
    def due_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.due]

    @property
    def clean(self) -> bool:
        return self.due_count == 0


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def check_rotation(
    env: Dict[str, str],
    timestamps: Dict[str, str],
    threshold_days: int = 90,
    secret_only: bool = True,
) -> RotateResult:
    """Evaluate each key in *env* against its last-rotated timestamp.

    Args:
        env: the parsed environment dict.
        timestamps: mapping of key -> ISO-8601 date string for last rotation.
        threshold_days: keys older than this many days are marked due.
        secret_only: when True, only flag keys that look like secrets.
    """
    from patchwork_env.redactor import _is_secret_key  # local import to avoid cycles

    now = datetime.now(tz=timezone.utc)
    entries: List[RotateEntry] = []

    for key in env:
        if secret_only and not _is_secret_key(key):
            continue

        ts_raw = timestamps.get(key)
        last_dt = _parse_iso(ts_raw) if ts_raw else None

        if last_dt is None:
            age_days = None
            due = True
            reason = "no rotation timestamp recorded"
        else:
            age_days = (now - last_dt).total_seconds() / 86400
            due = age_days > threshold_days
            reason = (
                f"last rotated {age_days:.1f} days ago (threshold {threshold_days}d)"
                if due
                else f"rotated {age_days:.1f} days ago — ok"
            )

        entries.append(
            RotateEntry(
                key=key,
                last_rotated=ts_raw,
                age_days=age_days,
                due=due,
                reason=reason,
            )
        )

    return RotateResult(entries=entries, threshold_days=threshold_days)
