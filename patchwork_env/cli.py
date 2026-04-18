"""CLI entry-point for patchwork-env."""
from __future__ import annotations
import argparse
import sys

from patchwork_env.parser import parse_env_file
from patchwork_env.differ import diff_envs
from patchwork_env.syncer import apply_diff, sync_summary
from patchwork_env.validator import validate_env
from patchwork_env.report import (
    render_text, render_summary, render_json,
    render_validation_text, render_validation_json,
)


def cmd_diff(args: argparse.Namespace) -> None:
    base = parse_env_file(args.base)
    target = parse_env_file(args.target)
    entries = diff_envs(base, target)
    if args.format == "json":
        print(render_json(entries, mask=args.mask))
    elif args.format == "summary":
        print(render_summary(entries))
    else:
        out = render_text(entries, mask=args.mask)
        print(out if out else "(no differences)")


def cmd_sync(args: argparse.Namespace) -> None:
    base = parse_env_file(args.base)
    target = parse_env_file(args.target)
    entries = diff_envs(base, target)
    updated = apply_diff(
        target,
        entries,
        overwrite=args.overwrite,
        add_missing=not args.no_add,
    )
    print(sync_summary(entries, overwrite=args.overwrite, add_missing=not args.no_add))
    if args.output:
        from patchwork_env.parser import serialize_env
        args.output.write(serialize_env(updated))
        args.output.close()


def cmd_validate(args: argparse.Namespace) -> None:
    env = parse_env_file(args.env)
    template = parse_env_file(args.template)
    result = validate_env(env, template, allow_extra=not args.strict)
    if args.format == "json":
        print(render_validation_json(result))
    else:
        print(render_validation_text(result))
    if not result.ok:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="patchwork-env", description="Diff and sync .env files.")
    sub = p.add_subparsers(dest="command", required=True)

    # diff
    d = sub.add_parser("diff", help="Show differences between two .env files")
    d.add_argument("base")
    d.add_argument("target")
    d.add_argument("--mask", action="store_true")
    d.add_argument("--format", choices=["text", "summary", "json"], default="text")
    d.set_defaults(func=cmd_diff)

    # sync
    s = sub.add_parser("sync", help="Sync base env into target")
    s.add_argument("base")
    s.add_argument("target")
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--no-add", action="store_true")
    s.add_argument("--output", type=argparse.FileType("w"), default=None)
    s.set_defaults(func=cmd_sync)

    # validate
    v = sub.add_parser("validate", help="Validate an env file against a template")
    v.add_argument("env")
    v.add_argument("template")
    v.add_argument("--strict", action="store_true", help="Disallow extra keys")
    v.add_argument("--format", choices=["text", "json"], default="text")
    v.set_defaults(func=cmd_validate)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
