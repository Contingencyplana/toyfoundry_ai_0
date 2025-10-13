"""Toyfoundry Forge ritual stub for the Purge phase."""
from __future__ import annotations

import argparse
import sys
from typing import Dict

from .ritual_logger import log_ritual_event

RITUAL_NAME = "purge"


def parse_kv(pairs: list[str] | None) -> Dict[str, str]:
    if not pairs:
        return {}
    result: Dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"Invalid metric specification: {item}")
        key, value = item.split("=", 1)
        result[key] = value
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Toyfoundry Purge ritual stub.")
    parser.add_argument("--batch-id", required=True, help="Batch identifier undergoing purge.")
    parser.add_argument("--reason", help="Reason for purge.")
    parser.add_argument("--metric", action="append", help="Additional metrics in key=value form.")
    parser.add_argument("--dry-run", action="store_true", help="Mark this invocation as a dry run.")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        metrics = parse_kv(args.metric)
        metadata = {
            "batch_id": args.batch_id,
            "reason": args.reason or "",
            "metrics": metrics,
            "dry_run": args.dry_run,
        }
        status = "dry_run" if args.dry_run else "completed"
        entry = log_ritual_event(RITUAL_NAME, status, metadata)
        if not args.quiet:
            print(f"Purge ritual logged: {entry}")
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Purge ritual failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
