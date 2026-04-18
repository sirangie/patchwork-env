"""CLI entry point for patchwork-env."""

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.differ import diff_envs, summary
from patchwork_env.report import render_text, render_json
from patchwork_env.syncer import apply_diff, sync_summary


def cmd_diff(args):
    base = parse_env_file(Path(args.base))
    target = parse_env_file(Path(args.target))
    entries = diff_envs(base, target, mask=args.mask)

    if args.format == "json":
        print(render_json(entries))
    else:
        print(render_text(entries))
        print()
        print(summary(entries))


def cmd_sync(args):
    base = parse_env_file(Path(args.base))
    target = parse_env_file(Path(args.target))
    entries = diff_envs(base, target, mask=False)

    updated = apply_diff(
        base,
        entries,
        overwrite=not args.no_overwrite,
        add_missing=not args.no_add,
    )

    out_path = Path(args.output) if args.output else Path(args.base)
    out_path.write_text(serialize_env(updated))
    print(sync_summary(entries, overwrite=not args.no_overwrite, add_missing=not args.no_add))
    print(f"Written to {out_path}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="patchwork-env",
        description="Diff and sync .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # diff
    p_diff = sub.add_parser("diff", help="Show differences between two .env files")
    p_diff.add_argument("base", help="Base .env file")
    p_diff.add_argument("target", help="Target .env file to compare against")
    p_diff.add_argument("--mask", action="store_true", help="Mask secret values in output")
    p_diff.add_argument("--format", choices=["text", "json"], default="text")
    p_diff.set_defaults(func=cmd_diff)

    # sync
    p_sync = sub.add_parser("sync", help="Sync base .env with values from target")
    p_sync.add_argument("base", help="Base .env file to update")
    p_sync.add_argument("target", help="Target .env file as source of truth")
    p_sync.add_argument("--output", "-o", help="Write result to this file instead of base")
    p_sync.add_argument("--no-overwrite", action="store_true", help="Skip changed keys")
    p_sync.add_argument("--no-add", action="store_true", help="Skip missing keys")
    p_sync.set_defaults(func=cmd_sync)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
