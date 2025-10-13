"""Telemetry quilt loom for Toyfoundry Alfa minting and rituals."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from tools.forge.forge_mint_alfa import TELEMETRY_FILE as MINT_TELEMETRY

DEFAULT_OUTPUT = Path(".toyfoundry") / "telemetry" / "quilt" / "quilt_rollup.json"
DEFAULT_COMPOSITE_OUTPUT = Path(".toyfoundry") / "telemetry" / "quilt" / "quilt_rollup_all.json"
RITUAL_TELEMETRY = Path(".toyfoundry") / "telemetry" / "forge_rituals.jsonl"


class QuiltError(RuntimeError):
    """Raised when the loom encounters invalid telemetry."""


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stitch Toyfoundry mint and ritual telemetry into quilt rollups.")
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=MINT_TELEMETRY,
        help="Path to the forge mint telemetry JSONL feed.",
    )
    parser.add_argument(
        "--ritual-telemetry",
        type=Path,
        default=RITUAL_TELEMETRY,
        help="Path to the forge ritual telemetry JSONL feed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination file for the mint rollup JSON.",
    )
    parser.add_argument(
        "--composite-output",
        type=Path,
        default=DEFAULT_COMPOSITE_OUTPUT,
        help="Destination file for the composite rollup JSON.",
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


def aggregate_mint(entries: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], int]:
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


def derive_operation_id(entry: Dict[str, Any]) -> str | None:
    metadata = entry.get("metadata") or {}
    candidates = [
        metadata.get("batch_id"),
        metadata.get("alfa_id"),
        metadata.get("operation_id"),
        entry.get("alfa_id"),
        entry.get("name"),
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return None


def update_last_updated(current: str | None, candidate: str | None) -> str | None:
    current_dt = iso_datetime(current) if current else None
    candidate_dt = iso_datetime(candidate) if candidate else None
    if current_dt is None:
        return candidate
    if candidate_dt is None:
        return current
    return candidate if candidate_dt > current_dt else current


def normalise_ritual_event(entry: Dict[str, Any]) -> Dict[str, Any]:
    metadata = entry.get("metadata") or {}
    return {
        "timestamp": entry.get("timestamp"),
        "status": entry.get("status", "unknown"),
        "metadata": metadata,
    }


def aggregate_composite(
    mint_rollup: Dict[str, Dict[str, Any]],
    ritual_entries: Iterable[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], int]:
    operations: Dict[str, Dict[str, Any]] = {}

    def ensure_operation(operation_id: str) -> Dict[str, Any]:
        return operations.setdefault(
            operation_id,
            {
                "mint": None,
                "rituals": {},
                "last_updated": None,
            },
        )

    for alfa_id, summary in mint_rollup.items():
        op = ensure_operation(alfa_id)
        op["mint"] = summary
        op["last_updated"] = update_last_updated(op["last_updated"], summary.get("last_seen"))

    processed = 0
    for entry in ritual_entries:
        operation_id = derive_operation_id(entry)
        if not operation_id:
            continue
        ritual = (entry.get("ritual") or "unknown").lower()
        op = ensure_operation(operation_id)
        ritual_bucket = op["rituals"].setdefault(
            ritual,
            {
                "total": 0,
                "dry_runs": 0,
                "completed": 0,
                "events": [],
            },
        )
        event = normalise_ritual_event(entry)
        ritual_bucket["events"].append(event)
        ritual_bucket["total"] += 1
        if event["metadata"].get("dry_run"):
            ritual_bucket["dry_runs"] += 1
        if event["status"] == "completed":
            ritual_bucket["completed"] += 1
        timestamp = event.get("timestamp")
        op["last_updated"] = update_last_updated(op.get("last_updated"), timestamp)
        processed += 1

    # Ensure event lists are chronological
    for op in operations.values():
        for ritual_data in op["rituals"].values():
            ritual_data["events"].sort(key=lambda evt: iso_datetime(evt.get("timestamp")) or datetime.min)

    return operations, processed


def write_rollup(rollup: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rollup, handle, indent=2, sort_keys=True)
        handle.write("\n")


def render_summary(
    mint_rollup: Dict[str, Dict[str, Any]],
    processed_mint: int,
    composite_rollup: Dict[str, Dict[str, Any]],
    processed_rituals: int,
    mint_output: Path,
    composite_output: Path,
) -> None:
    print(f"Processed {processed_mint} mint telemetry events across {len(mint_rollup)} alfa runs.")
    if not mint_rollup:
        print("No mint rollup entries generated. Check that mint telemetry exists.")
    else:
        for alfa_id in sorted(mint_rollup):
            summary = mint_rollup[alfa_id]
            print(
                f"  - {alfa_id}: dry_runs={summary['dry_runs']} minted={summary['mint_runs']} "
                f"latest={summary['latest_status']}"
            )
    print(f"Mint quilt rollup written to {mint_output}")

    ritual_counter: Counter[str] = Counter()
    for operation in composite_rollup.values():
        ritual_counter.update(operation["rituals"].keys())

    print(
        f"Processed {processed_rituals} ritual telemetry events across {len(composite_rollup)} operations."
    )
    if composite_rollup:
        for ritual, count in sorted(ritual_counter.items()):
            print(f"  - {ritual}: {count} operations")
    print(f"Composite quilt rollup written to {composite_output}")


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        mint_entries = read_telemetry(args.telemetry)
        mint_rollup, processed_mint = aggregate_mint(mint_entries)

        ritual_entries = read_telemetry(args.ritual_telemetry)
        composite_rollup, processed_rituals = aggregate_composite(mint_rollup, ritual_entries)

        write_rollup(mint_rollup, args.output)
        write_rollup(composite_rollup, args.composite_output)
        render_summary(
            mint_rollup,
            processed_mint,
            composite_rollup,
            processed_rituals,
            args.output,
            args.composite_output,
        )
        return 0
    except QuiltError as exc:
        print(f"Quilt loom failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unexpected quilt loom error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
