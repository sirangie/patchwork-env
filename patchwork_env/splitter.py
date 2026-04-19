"""Split a single .env into multiple files by prefix or tag."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    buckets: Dict[str, Dict[str, str]]
    unmatched: Dict[str, str]
    prefixes: List[str]

    @property
    def bucket_names(self) -> List[str]:
        return list(self.buckets.keys())

    def keys_in(self, bucket: str) -> List[str]:
        return list(self.buckets.get(bucket, {}).keys())

    @property
    def total_keys(self) -> int:
        total = sum(len(v) for v in self.buckets.values())
        return total + len(self.unmatched)


def split_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    infer: bool = True,
    separator: str = "_",
) -> SplitResult:
    """Split env dict into buckets by key prefix.

    Args:
        env: flat key/value dict.
        prefixes: explicit list of prefixes to split on.
        infer: if True and prefixes is None, infer prefixes from keys.
        separator: character used to split prefix from rest of key.
    """
    if prefixes is None and infer:
        prefixes = _infer_prefixes(list(env.keys()), separator)
    elif prefixes is None:
        prefixes = []

    buckets: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    unmatched: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix + separator):
                buckets[prefix][key] = value
                matched = True
                break
        if not matched:
            unmatched[key] = value

    # drop empty buckets
    buckets = {k: v for k, v in buckets.items() if v}

    return SplitResult(buckets=buckets, unmatched=unmatched, prefixes=prefixes)


def _infer_prefixes(keys: List[str], separator: str = "_") -> List[str]:
    from collections import Counter
    counts: Counter = Counter()
    for key in keys:
        if separator in key:
            counts[key.split(separator)[0]] += 1
    return [p for p, c in counts.items() if c >= 2]
