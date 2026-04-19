"""Pin specific env keys to fixed values, preventing them from being changed by sync or patch."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinEntry:
    key: str
    pinned_value: str
    attempted_value: Optional[str] = None
    blocked: bool = False

    def __repr__(self) -> str:
        if self.blocked:
            return f"PinEntry({self.key!r} pinned={self.pinned_value!r} blocked {self.attempted_value!r})"
        return f"PinEntry({self.key!r} pinned={self.pinned_value!r})"


@dataclass
class PinResult:
    env: Dict[str, str]
    entries: List[PinEntry] = field(default_factory=list)

    @property
    def blocked_count(self) -> int:
        return sum(1 for e in self.entries if e.blocked)

    @property
    def pinned_keys(self) -> List[str]:
        return [e.key for e in self.entries]


def pin_env(
    env: Dict[str, str],
    pins: Dict[str, str],
    incoming: Optional[Dict[str, str]] = None,
) -> PinResult:
    """Apply pins to env. If incoming is provided, block any incoming changes to pinned keys."""
    result = dict(env)
    entries: List[PinEntry] = []

    for key, pinned_value in pins.items():
        attempted = None
        blocked = False

        if incoming is not None and key in incoming and incoming[key] != pinned_value:
            attempted = incoming[key]
            blocked = True

        result[key] = pinned_value
        entries.append(PinEntry(key=key, pinned_value=pinned_value, attempted_value=attempted, blocked=blocked))

    return PinResult(env=result, entries=entries)
