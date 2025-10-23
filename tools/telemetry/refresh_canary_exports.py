"""Utility to refresh Toyfoundry canary export artefacts.

This script re-normalises JSON and CSV exports for canary batches, rewrites
associated SHA256 sidecars, and updates build/manifest metadata timestamps.
Run after schema remediation to keep per-order canary bundles aligned with
Order 021 expectations.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List

EXPORT_FIELDS = [
    "schema_version",
    "batch_id",
    "ritual",
    "units_processed",
    "status",
    "duration_ms",
]

UTC_NOW = _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0)
TIMESTAMP = UTC_NOW.isoformat().replace("+00:00", "Z")


def _load_records(json_path: Path) -> List[Dict[str, object]]:
    records = json.loads(json_path.read_text(encoding="utf-8"))
    records = [dict(record) for record in records]
    records.sort(key=lambda record: (record["batch_id"], record["ritual"], record["status"]))
    return records


def _write_json(json_path: Path, records: Iterable[Dict[str, object]]) -> None:
    json_path.write_text(
        json.dumps(list(records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_csv(csv_path: Path, records: Iterable[Dict[str, object]]) -> None:
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record[field] for field in EXPORT_FIELDS})


def _write_checksum(artifact: Path) -> str:
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest().upper()
    checksum_path = artifact.with_suffix(artifact.suffix + ".sha256")
    checksum_path.write_text(f"\nHash\n----\n{digest}\n", encoding="ascii")
    return digest


def _update_manifest(manifest_path: Path, records: List[Dict[str, object]], checksums: Dict[str, str]) -> None:
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generated_at"] = TIMESTAMP

    counts = manifest.get("counts")
    if isinstance(counts, dict):
        counts["records"] = len(records)
        counts.setdefault("batches", len({rec["batch_id"] for rec in records}))

    artifacts = manifest.get("artifacts")
    if isinstance(artifacts, list):
        for entry in artifacts:
            if not isinstance(entry, dict):
                continue
            filename = entry.get("filename")
            if not filename and entry.get("path"):
                filename = Path(entry["path"]).name
            if filename and filename in checksums:
                entry["sha256"] = checksums[filename]

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _update_build_info(build_info_path: Path, records: List[Dict[str, object]], checksums: Dict[str, str]) -> None:
    if not build_info_path.exists():
        return
    build_info = json.loads(build_info_path.read_text(encoding="utf-8"))
    build_info["timestamp"] = TIMESTAMP

    counts = build_info.get("counts")
    if isinstance(counts, dict):
        counts["records"] = len(records)
        counts["units_total"] = sum(int(record["units_processed"]) for record in records)

    if "batch_contents" in build_info:
        build_info["batch_contents"] = sorted({record["batch_id"] for record in records})
    if "canary_batches" in build_info:
        build_info["canary_batches"] = sorted({record["batch_id"] for record in records})
    if "batch_count" in build_info:
        build_info["batch_count"] = len({record["batch_id"] for record in records})

    artifacts = build_info.get("artifacts")
    if isinstance(artifacts, list):
        for entry in artifacts:
            if not isinstance(entry, dict):
                continue
            path_str = entry.get("path")
            filename = Path(path_str).name if path_str else None
            if filename and filename in checksums:
                entry["sha256"] = checksums[filename]
    elif isinstance(artifacts, dict):
        for filename in list(artifacts.keys()):
            if filename in checksums:
                artifacts[filename] = checksums[filename]

    build_info_path.write_text(json.dumps(build_info, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def refresh_directory(directory: Path) -> Dict[str, str]:
    json_path = directory / "composite_export.json"
    csv_path = directory / "composite_export.csv"
    records = _load_records(json_path)
    _write_json(json_path, records)
    _write_csv(csv_path, records)

    checksums = {
        json_path.name: _write_checksum(json_path),
        csv_path.name: _write_checksum(csv_path),
    }

    _update_manifest(directory / "export_manifest.json", records, checksums)
    _update_build_info(directory / "build_info.json", records, checksums)
    return checksums


def refresh_top_level(source_json: Path, dest_json: Path, dest_csv: Path, build_info: Path | None = None) -> None:
    records = _load_records(source_json)
    _write_json(dest_json, records)
    _write_csv(dest_csv, records)

    checksums = {
        dest_json.name: _write_checksum(dest_json),
        dest_csv.name: _write_checksum(dest_csv),
    }

    if build_info:
        _update_build_info(build_info, records, checksums)


def main() -> None:
    base = Path(".toyfoundry/telemetry/quilt/exports")

    directories = [
        base / "order028_canary",
        base / "order030_canary_b1",
        base / "order030_canary_b2",
        base / "canary_c1",
    ]

    for directory in directories:
        refresh_directory(directory)

    refresh_top_level(
        base / "order030_canary_b1" / "composite_export.json",
        base / "canary_batch_b1.json",
        base / "canary_batch_b1.csv",
        base / "build_info_b1.json",
    )
    refresh_top_level(
        base / "order030_canary_b2" / "composite_export.json",
        base / "canary_batch_b2.json",
        base / "canary_batch_b2.csv",
        base / "build_info_b2.json",
    )


if __name__ == "__main__":
    main()
