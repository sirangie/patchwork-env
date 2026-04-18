"""Sync logic: apply a diff to a target env dict, producing a merged result."""

from typing import Dict, Optional
from patchwork_env.differ import DiffEntry


def apply_diff(
    target: Dict[str, str],
    diff: list[DiffEntry],
    *,
    overwrite_changed: bool = True,
    add_missing: bool = True,
    remove_deleted: bool = False,
) -> Dict[str, str]:
    """Return a new env dict with the diff applied to *target*.

    Args:
        target: The destination env (e.g. production).
        diff: Output from differ.diff_envs(source, target).
        overwrite_changed: If True, update keys whose values differ.
        add_missing: If True, add keys present in source but not target.
        remove_deleted: If True, remove keys absent in source.

    Returns:
        A new dict representing the synced environment.
    """
    result = dict(target)

    for entry in diff:
        if entry.status == "changed" and overwrite_changed:
            result[entry.key] = entry.source_value
        elif entry.status == "added" and add_missing:
            result[entry.key] = entry.source_value
        elif entry.status == "removed" and remove_deleted:
            result.pop(entry.key, None)
        # "unchanged" — nothing to do

    return result


def sync_summary(diff: list[DiffEntry], *, overwrite_changed: bool, add_missing: bool, remove_deleted: bool) -> str:
    """Human-readable one-liner describing what sync will do."""
    counts = {"changed": 0, "added": 0, "removed": 0, "unchanged": 0}
    for entry in diff:
        counts[entry.status] = counts.get(entry.status, 0) + 1

    parts = []
    if overwrite_changed and counts["changed"]:
        parts.append(f"{counts['changed']} updated")
    if add_missing and counts["added"]:
        parts.append(f"{counts['added']} added")
    if remove_deleted and counts["removed"]:
        parts.append(f"{counts['removed']} removed")
    if not parts:
        return "Nothing to sync."
    return "Sync will apply: " + ", ".join(parts) + "."
