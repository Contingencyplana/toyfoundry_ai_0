"""Telemetry quilt loom for Toyfoundry Alfa minting and rituals."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from tools.forge.forge_mint_alfa import TELEMETRY_FILE as MINT_TELEMETRY

DEFAULT_OUTPUT = Path(".toyfoundry") / "telemetry" / "quilt" / "quilt_rollup.json"
DEFAULT_COMPOSITE_OUTPUT = Path(".toyfoundry") / "telemetry" / "quilt" / "quilt_rollup_all.json"
DEFAULT_EXPORT_DIR = Path(".toyfoundry") / "telemetry" / "quilt" / "exports"
RITUAL_TELEMETRY = Path(".toyfoundry") / "telemetry" / "forge_rituals.jsonl"

SCHEMA_VERSION = "1.0"
MAX_DURATION_MS = 300_000
RITUAL_ALIASES = {
    "drill": "forge",
    "forge": "forge",
}
VALID_RITUALS = {"forge", "parade", "purge", "promote"}
EVENT_STATUS_MAP = {
    "completed": "success",
    "success": "success",
    "succeeded": "success",
    "failed": "failure",
    "failure": "failure",
    "error": "failure",
    "dry_run": "partial",
    "partial": "partial",
    "unknown": "partial",
}
MINT_STATUS_MAP = {
    "minted": "success",
    "draft": "partial",
    "failed": "failure",
    "failure": "failure",
    "error": "failure",
}


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
    parser.add_argument(
        "--export",
        action="store_true",
        help="Generate JSON and CSV exports from the composite rollup.",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Directory where export artefacts are written when --export is supplied.",
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


EXPORT_FIELDS = [
    "schema_version",
    "batch_id",
    "ritual",
    "units_processed",
    "status",
    "duration_ms",
]


def normalise_status(raw_status: Any, mapping: Dict[str, str], default: str = "partial") -> str:
    if raw_status is None:
        return default
    key = str(raw_status).strip().lower()
    return mapping.get(key, default)


def normalise_ritual(raw_ritual: Any) -> str:
    if raw_ritual is None:
        return "forge"
    key = str(raw_ritual).strip().lower()
    canonical = RITUAL_ALIASES.get(key, key)
    if canonical not in VALID_RITUALS:
        return "forge"
    return canonical


def extract_units(metadata: Dict[str, Any], fallback: int = 1) -> int:
    candidates = [
        metadata.get("units_processed"),
        metadata.get("units"),
        metadata.get("count"),
    ]
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    candidates.extend([metrics.get("units_processed"), metrics.get("units"), metrics.get("count")])
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            value = int(candidate)
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    return max(1, fallback)


def extract_duration(metadata: Dict[str, Any]) -> int:
    candidates = [
        metadata.get("duration_ms"),
        metadata.get("duration"),
    ]
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    candidates.extend([metrics.get("duration_ms"), metrics.get("duration"), metrics.get("durationMillis")])
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            value = int(candidate)
        except (TypeError, ValueError):
            continue
        if value < 0:
            value = 0
        if value > MAX_DURATION_MS:
            value = MAX_DURATION_MS
        return value
    return 0


def flatten_composite(composite_rollup: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for operation_id, data in sorted(composite_rollup.items()):
        mint = data.get("mint") or {}
        rituals = data.get("rituals") or {}
        events_emitted = False

        for ritual_name, ritual_data in sorted(rituals.items()):
            events = ritual_data.get("events") or []
            if not events:
                continue
            normalised_ritual = normalise_ritual(ritual_name)
            for event in events:
                metadata = event.get("metadata") or {}
                batch_id = str(metadata.get("batch_id") or operation_id)
                units_processed = extract_units(metadata)
                duration_ms = extract_duration(metadata)
                status = normalise_status(event.get("status"), EVENT_STATUS_MAP)
                if metadata.get("dry_run"):
                    status = "partial"
                record = {
                    "schema_version": SCHEMA_VERSION,
                    "batch_id": batch_id,
                    "ritual": normalised_ritual,
                    "units_processed": units_processed,
                    "status": status,
                    "duration_ms": duration_ms,
                }
                records.append(record)
                events_emitted = True

        if not events_emitted:
            # Preserve batches that have only mint telemetry by emitting a synthetic forge record.
            batch_id = str(operation_id)
            status = normalise_status(mint.get("latest_status"), MINT_STATUS_MAP, default="partial")
            units_processed = mint.get("mint_runs", 0)
            try:
                units_processed_int = int(units_processed)
            except (TypeError, ValueError):
                units_processed_int = 0
            record = {
                "schema_version": SCHEMA_VERSION,
                "batch_id": batch_id,
                "ritual": "forge",
                "units_processed": max(1, units_processed_int or 1),
                "status": status,
                "duration_ms": 0,
            }
            records.append(record)

    records.sort(key=lambda item: (item["batch_id"], item["ritual"], item["status"]))
    return records


def write_checksum(artifact_path: Path) -> str:
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest().upper()
    checksum_path = artifact_path.with_suffix(artifact_path.suffix + ".sha256")
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    with checksum_path.open("w", encoding="ascii") as handle:
        handle.write("\nHash\n----\n")
        handle.write(digest)
        handle.write("\n")
    return digest


def update_metadata_checksums(export_dir: Path, checksums: Dict[str, str]) -> None:
    timestamp = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    manifest_path = export_dir / "export_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["generated_at"] = timestamp

        artifacts_block = manifest.get("artifacts")
        if isinstance(artifacts_block, list):
            for artifact in artifacts_block:
                filename = artifact.get("filename") if isinstance(artifact, dict) else None
                if filename and filename in checksums:
                    artifact["sha256"] = checksums[filename]

        checksum_block = manifest.get("checksums")
        if isinstance(checksum_block, dict):
            for filename, digest in checksums.items():
                if filename in checksum_block:
                    checksum_block[filename] = digest

        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    build_info_path = export_dir / "build_info.json"
    if build_info_path.exists():
        build_info = json.loads(build_info_path.read_text(encoding="utf-8"))
        build_info["timestamp"] = timestamp

        artifacts_block = build_info.get("artifacts")
        if isinstance(artifacts_block, list):
            for artifact in artifacts_block:
                path_str = artifact.get("path") if isinstance(artifact, dict) else None
                filename = Path(path_str).name if path_str else None
                if filename and filename in checksums:
                    artifact["sha256"] = checksums[filename]
        elif isinstance(artifacts_block, dict):
            for filename, digest in checksums.items():
                if filename in artifacts_block:
                    artifacts_block[filename] = digest

        build_info_path.write_text(
            json.dumps(build_info, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def write_exports(records: List[Dict[str, Any]], export_dir: Path) -> Tuple[Path, Path, Dict[str, str]]:
    export_dir.mkdir(parents=True, exist_ok=True)
    json_path = export_dir / "composite_export.json"
    csv_path = export_dir / "composite_export.csv"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    checksums = {
        json_path.name: write_checksum(json_path),
        csv_path.name: write_checksum(csv_path),
    }
    update_metadata_checksums(export_dir, checksums)

    return json_path, csv_path, checksums


def render_summary(
    mint_rollup: Dict[str, Dict[str, Any]],
    processed_mint: int,
    composite_rollup: Dict[str, Dict[str, Any]],
    processed_rituals: int,
    mint_output: Path,
    composite_output: Path,
    export_paths: Tuple[Path, Path] | None,
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

    if export_paths:
        json_path, csv_path = export_paths
        print("Exports written:")
        print(f"  - JSON: {json_path}")
        print(f"  - CSV: {csv_path}")


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        mint_entries = read_telemetry(args.telemetry)
        mint_rollup, processed_mint = aggregate_mint(mint_entries)

        ritual_entries = read_telemetry(args.ritual_telemetry)
        composite_rollup, processed_rituals = aggregate_composite(mint_rollup, ritual_entries)

        write_rollup(mint_rollup, args.output)
        write_rollup(composite_rollup, args.composite_output)
        export_paths: Tuple[Path, Path] | None = None
        if args.export:
            records = flatten_composite(composite_rollup)
            json_path, csv_path, _checksums = write_exports(records, args.export_dir)
            export_paths = (json_path, csv_path)
        render_summary(
            mint_rollup,
            processed_mint,
            composite_rollup,
            processed_rituals,
            args.output,
            args.composite_output,
            export_paths,
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
