"""CLI entry point for patchwork-env."""
from __future__ import annotations

import argparse
import sys

from patchwork_env.parser import parse_env_file, serialize_env
from patchwork_env.differ import diff_envs
from patchwork_env.syncer import apply_diff, sync_summary
from patchwork_env.validator import validate
from patchwork_env.report import (
    render_text,
    render_summary,
    render_json,
    render_validation_text,
    render_validation_json,
    render_audit_text,
)
from patchwork_env.auditor import record_diff, record_sync, read_audit_log


def cmd_diff(args: argparse.Namespace) -> None:
    src = parse_env_file(args.source)
    tgt = parse_env_file(args.target)
    entries = diff_envs(src, tgt, mask=args.mask)
    if args.format == "json":
        print(render_json(entries))
    else:
        print(render_text(entries))
        print(render_summary(entries))
    if args.audit:
        record_diff(entries, args.source, args.target, audit_file=args.audit)


def cmd_sync(args: argparse.Namespace) -> None:
    src = parse_env_file(args.source)
    tgt = parse_env_file(args.target)
    entries = diff_envs(src, tgt)
    updated, applied, skipped = apply_diff(
        tgt, entries, overwrite=args.overwrite, add_missing=not args.no_add
    )
    with open(args.target, "w", encoding="utf-8") as fh:
        fh.write(serialize_env(updated))
    print(sync_summary(applied, skipped))
    if args.audit:
        record_sync(applied, skipped, args.target, audit_file=args.audit)


def cmd_validate(args: argparse.Namespace) -> None:
    env = parse_env_file(args.env)
    schema = parse_env_file(args.schema)
    result = validate(env, schema)
    if args.format == "json":
        print(render_validation_json(result))
    else:
        print(render_validation_text(result))
    if not result.ok:
        sys.exit(1)


def cmd_audit(args: argparse.Namespace) -> None:
    events = read_audit_log(audit_file=args.audit_file)
    print(render_audit_text(events))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="patchwork-env", description="Diff and sync .env files.")
    sub = p.add_subparsers(dest="command")

    diff_p = sub.add_parser("diff", help="Show differences between two .env files")
    diff_p.add_argument("source")
    diff_p.add_argument("target")
    diff_p.add_argument("--mask", action="store_true")
    diff_p.add_argument("--format", choices=["text", "json"], default="text")
    diff_p.add_argument("--audit", metavar="FILE", default=None)

    sync_p = sub.add_parser("sync", help="Sync source keys into target")
    sync_p.add_argument("source")
    sync_p.add_argument("target")
    sync_p.add_argument("--overwrite", action="store_true")
    sync_p.add_argument("--no-add", action="store_true")
    sync_p.add_argument("--audit", metavar="FILE", default=None)

    val_p = sub.add_parser("validate", help="Validate a .env against a schema")
    val_p.add_argument("env")
    val_p.add_argument("schema")
    val_p.add_argument("--format", choices=["text", "json"], default="text")

    audit_p = sub.add_parser("audit", help="Show audit log")
    audit_p.add_argument("--audit-file", default=None)

    return p


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {"diff": cmd_diff, "sync": cmd_sync, "validate": cmd_validate, "audit": cmd_audit}
    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()
