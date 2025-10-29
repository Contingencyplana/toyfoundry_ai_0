"""Emit factory orders for Toyfoundry Alfa Two translator payloads."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from tools.factory_order_emitter import (
    PayloadValidationError,
    build_factory_order,
    load_translator_payload,
    write_factory_order,
)

DEFAULT_INPUT_DIR = Path("tests/alfa_two")
DEFAULT_OUTPUT_DIR = Path("exchange/orders/outbox/emoji_runtime")


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("TF-ALFA2-%Y%m%d-%H%M")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote one or more translator payloads into factory-order@1.0 documents for Alfa Two",
    )
    parser.add_argument(
        "payloads",
        nargs="*",
        type=Path,
        help="Explicit translator payload paths to promote. Defaults to all fixtures in --input-dir.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory to scan for translator payloads when none are passed explicitly.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination directory for emitted factory orders.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier used to build order IDs (defaults to TF-ALFA2-<timestamp>).",
    )
    parser.add_argument(
        "--issued-by",
        default="toyfoundry_ai_0",
        help="Workspace issuing the factory order.",
    )
    parser.add_argument(
        "--target",
        default="toyfoundry_ai_0",
        help="Factory order target workspace.",
    )
    parser.add_argument(
        "--priority",
        default="standard",
        help="Factory order priority flag.",
    )
    parser.add_argument(
        "--narrator",
        help="Optional War Office narrator persona to embed in metadata.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate payloads without writing files.",
    )
    parser.add_argument(
        "--summary-override",
        help="Override the lore-facing summary (must align with narrator output).",
    )
    return parser.parse_args(argv)


def _discover_payloads(payloads: Iterable[Path], input_dir: Path) -> List[Path]:
    explicit = [path for path in payloads if path.exists()]
    if explicit:
        return explicit

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    discovered = sorted(
        path
        for path in input_dir.glob("*.json")
        if "missing" not in path.name and "invalid" not in path.stem
    )
    if not discovered:
        raise FileNotFoundError(f"No translator payloads found in {input_dir}")
    return discovered


def emit_orders(args: argparse.Namespace) -> int:
    run_id = args.run_id or _default_run_id()
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    payload_paths = _discover_payloads(args.payloads, args.input_dir)

    for index, payload_path in enumerate(payload_paths, start=1):
        try:
            translator = load_translator_payload(payload_path)
            order_id = f"{run_id}-{index:02d}"
            payload = build_factory_order(
                translator,
                order_id=order_id,
                issued_by=args.issued_by,
                target=args.target,
                priority=args.priority,
                timestamp_issued=timestamp,
                summary_override=args.summary_override,
                narrator=args.narrator,
                extra_fields=None,
            )

            destination = output_dir / f"{order_id}.json"
            if args.dry_run:
                print(json.dumps(payload, indent=2))
                print(f"[dry-run] {payload_path} -> {order_id}")
            else:
                write_factory_order(payload, destination)
                print(f"Emitted {destination}")
        except PayloadValidationError as exc:
            print(f"Emission aborted for {payload_path}: {exc}")
            return 1

    return 0


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return emit_orders(args)
    except FileNotFoundError as exc:
        print(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
