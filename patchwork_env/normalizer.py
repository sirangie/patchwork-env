from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeOp:
    key: str
    old_value: str
    new_value: str
    action: str  # 'strip', 'upper_key', 'lower_key', 'none'

    def __repr__(self) -> str:
        return f"NormalizeOp({self.key!r}, {self.action})"


@dataclass
class NormalizeResult:
    ops: List[NormalizeOp] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def changed_count(self) -> int:
        return sum(1 for op in self.ops if op.action != 'none')

    @property
    def unchanged_count(self) -> int:
        return sum(1 for op in self.ops if op.action == 'none')

    @property
    def changed_keys(self) -> List[str]:
        return [op.key for op in self.ops if op.action != 'none']


def normalize_env(
    env: Dict[str, str],
    strip_values: bool = True,
    key_case: str = "upper",  # 'upper', 'lower', or 'preserve'
) -> NormalizeResult:
    """Normalize keys and values in an env dict."""
    ops: List[NormalizeOp] = []
    out: Dict[str, str] = {}

    for raw_key, raw_val in env.items():
        actions: List[str] = []
        val = raw_val
        key = raw_key

        if strip_values and val != val.strip():
            val = val.strip()
            actions.append("strip")

        if key_case == "upper" and key != key.upper():
            key = key.upper()
            actions.append("upper_key")
        elif key_case == "lower" and key != key.lower():
            key = key.lower()
            actions.append("lower_key")

        action = ",".join(actions) if actions else "none"
        ops.append(NormalizeOp(key=key, old_value=raw_val, new_value=val, action=action))
        out[key] = val

    return NormalizeResult(ops=ops, env=out)
