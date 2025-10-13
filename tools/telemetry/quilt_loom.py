"""Telemetry quilt loom for Toyfoundry Alfa minting."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from tools.forge.forge_mint_alfa import TELEMETRY_FILE as MINT_TELEMETRY

DEFAULT_OUTPUT = Path(".toyfoundry") / "telemetry" / "quilt" / "quilt_rollup.json"


class QuiltError(RuntimeError):
    """Raised when the loom encounters invalid telemetry."""


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stitch Toyfoundry mint telemetry into a quilt rollup.")
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=MINT_TELEMETRY,
        help="Path to the forge mint telemetry JSONL feed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination file for the quilt rollup JSON.",
    )
    return parser.parse_args(argv)


def read_telemetry(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise QuiltError(f"Malformed telemetry at {path}:{line_no}: {exc}") from exc
    return entries


def iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QuiltError(f"Invalid timestamp '{value}'") from exc


def aggregate(entries: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], int]:
    rollup: Dict[str, Dict[str, Any]] = {}
    processed = 0
    for entry in entries:
        alfa_id = entry.get("alfa_id")
        if not alfa_id:
            continue
        processed += 1
        summary = rollup.setdefault(
            alfa_id,
            {
                "name": entry.get("name", ""),
                "dry_runs": 0,
                "mint_runs": 0,
                "latest_status": entry.get("status", "unknown"),
                "first_seen": entry.get("timestamp"),
                "last_seen": entry.get("timestamp"),
                "last_output_path": entry.get("output_path"),
            },
        )

        if not summary["name"] and entry.get("name"):
            summary["name"] = entry["name"]

        timestamp = entry.get("timestamp")
        seen_time = iso_datetime(timestamp)
        first_time = iso_datetime(summary.get("first_seen"))
        last_time = iso_datetime(summary.get("last_seen"))

        if first_time is None or (seen_time is not None and seen_time < first_time):
            summary["first_seen"] = timestamp
        if last_time is None or (seen_time is not None and seen_time > last_time):
            summary["last_seen"] = timestamp

        if entry.get("dry_run"):
            summary["dry_runs"] += 1
        else:
            summary["mint_runs"] += 1

        summary["latest_status"] = entry.get("status", summary["latest_status"])
        if entry.get("output_path"):
            summary["last_output_path"] = entry.get("output_path")

    return rollup, processed


def write_rollup(rollup: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rollup, handle, indent=2, sort_keys=True)
        handle.write("\n")


def render_summary(rollup: Dict[str, Dict[str, Any]], processed_events: int, output_path: Path) -> None:
    print(f"Processed {processed_events} mint telemetry events across {len(rollup)} alfa runs.")
    if not rollup:
        print("No rollup entries generated. Check that mint telemetry exists.")
    else:
        for alfa_id in sorted(rollup):
            summary = rollup[alfa_id]
            print(
                f"  - {alfa_id}: dry_runs={summary['dry_runs']} minted={summary['mint_runs']} "
                f"latest={summary['latest_status']}"
            )
    print(f"Quilt rollup written to {output_path}")


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        entries = read_telemetry(args.telemetry)
        rollup, processed = aggregate(entries)
        write_rollup(rollup, args.output)
        render_summary(rollup, processed, args.output)
        return 0
    except QuiltError as exc:
        print(f"Quilt loom failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unexpected quilt loom error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
