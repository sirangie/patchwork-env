"""Transform env values: uppercase keys, lowercase values, strip whitespace, etc."""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformOp:
    key: str
    original: str
    result: str
    transform: str
    changed: bool

    def __repr__(self) -> str:
        return f"TransformOp({self.key!r}, {self.transform!r}, changed={self.changed})"


@dataclass
class TransformResult:
    env: Dict[str, str]
    ops: List[TransformOp] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for op in self.ops if op.changed)

    @property
    def unchanged_count(self) -> int:
        return sum(1 for op in self.ops if not op.changed)


_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "uppercase": str.upper,
    "lowercase": str.lower,
    "strip": str.strip,
    "strip_quotes": lambda v: v.strip("'\"")
}


def transform_env(
    env: Dict[str, str],
    transforms: List[str],
    keys: Optional[List[str]] = None,
) -> TransformResult:
    """Apply one or more named transforms to env values.

    Args:
        env: source key/value pairs
        transforms: ordered list of transform names to apply
        keys: if given, only transform these keys; otherwise all keys
    """
    unknown = [t for t in transforms if t not in _TRANSFORMS]
    if unknown:
        raise ValueError(f"Unknown transforms: {unknown}. Available: {list(_TRANSFORMS)}")

    target_keys = set(keys) if keys else set(env.keys())
    result_env: Dict[str, str] = {}
    ops: List[TransformOp] = []

    for k, v in env.items():
        if k in target_keys:
            new_v = v
            applied = []
            for t in transforms:
                new_v = _TRANSFORMS[t](new_v)
                applied.append(t)
            label = "+".join(applied)
            ops.append(TransformOp(key=k, original=v, result=new_v, transform=label, changed=(new_v != v)))
            result_env[k] = new_v
        else:
            result_env[k] = v

    return TransformResult(env=result_env, ops=ops)
