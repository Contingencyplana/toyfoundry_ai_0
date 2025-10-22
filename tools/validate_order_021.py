"""Schema and data-quality validator for Order 021 exports."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REQUIRED_FIELDS = {
    "schema_version": str,
    "batch_id": str,
    "ritual": str,
    "units_processed": int,
    "status": str,
    "duration_ms": int,
}

ALLOWED_RITUALS = {"forge", "parade", "purge", "promote"}
ALLOWED_STATUS = {"success", "failure", "partial"}
SCHEMA_VERSION = "1.0"
DURATION_RANGE = (0, 300_000)


class ValidationIssue(Exception):
    """Raised when the export fails Order 021 checks."""


class ValidationSummary:
    """Collects pass/fail counts for reporting."""

    def __init__(self) -> None:
        self.records = 0
        self.successful = 0
        self.failures: List[str] = []

    def add_success(self) -> None:
        self.records += 1
        self.successful += 1

    def add_failure(self, reason: str) -> None:
        self.records += 1
        self.failures.append(reason)

    def has_failures(self) -> bool:
        return bool(self.failures)

    def __str__(self) -> str:  # pragma: no cover - human-readable output
        if self.failures:
            return (
                f"Validation failed for {self.successful}/{self.records} records.\n"
                + "\n".join(f"  - {failure}" for failure in self.failures[:10])
            )
        return f"Validation passed for all {self.successful} records."


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Toyfoundry exports against Order 021 schema")
    parser.add_argument(
        "json_export",
        type=Path,
        nargs="?",
        default=Path(".toyfoundry") / "telemetry" / "quilt" / "exports" / "composite_export.json",
        help="Path to composite_export.json",
    )
    parser.add_argument(
        "--csv",
        dest="csv_export",
        type=Path,
        help="Optional path to composite_export.csv for header validation",
    )
    return parser.parse_args(argv)


def load_json_exports(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        raise ValidationIssue(f"JSON export not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - IO guard
        raise ValidationIssue(f"Malformed JSON export: {exc}") from exc
    if not isinstance(data, list):
        raise ValidationIssue("Expected JSON export to be a list of records")
    if not data:
        raise ValidationIssue("JSON export is empty")
    return data


def validate_record(index: int, record: Dict[str, object]) -> Tuple[bool, str | None]:
    for field, field_type in REQUIRED_FIELDS.items():
        if field not in record:
            return False, f"Record {index}: missing field '{field}'"
        value = record[field]
        if field_type is int:
            if not isinstance(value, int):
                return False, f"Record {index}: field '{field}' must be an integer"
        elif field_type is str:
            if not isinstance(value, str):
                return False, f"Record {index}: field '{field}' must be a string"

    if record["schema_version"] != SCHEMA_VERSION:
        return False, f"Record {index}: schema_version '{record['schema_version']}' != '{SCHEMA_VERSION}'"
    if record["ritual"] not in ALLOWED_RITUALS:
        return False, f"Record {index}: ritual '{record['ritual']}' not in {sorted(ALLOWED_RITUALS)}"
    if record["status"] not in ALLOWED_STATUS:
        return False, f"Record {index}: status '{record['status']}' not in {sorted(ALLOWED_STATUS)}"

    units = record["units_processed"]
    if units <= 0:
        return False, f"Record {index}: units_processed {units} must be > 0"

    duration = record["duration_ms"]
    low, high = DURATION_RANGE
    if not (low <= duration <= high):
        return False, f"Record {index}: duration_ms {duration} outside [{low}, {high}]"

    return True, None


def validate_csv_headers(path: Path) -> None:
    if not path:
        return
    if not path.exists():
        raise ValidationIssue(f"CSV export not found: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            raise ValidationIssue("CSV export is empty") from None
    expected_order = list(REQUIRED_FIELDS.keys())
    if header != expected_order:
        raise ValidationIssue(
            "CSV header mismatch: expected "
            + ",".join(expected_order)
            + " but found "
            + ",".join(header)
        )


def run_validation(json_path: Path, csv_path: Path | None) -> ValidationSummary:
    records = load_json_exports(json_path)
    summary = ValidationSummary()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            summary.add_failure(f"Record {index}: expected object, found {type(record).__name__}")
            continue
        ok, reason = validate_record(index, record)
        if ok:
            summary.add_success()
        else:
            summary.add_failure(reason or f"Record {index}: unknown validation error")
    if summary.has_failures():
        raise ValidationIssue(str(summary))
    validate_csv_headers(csv_path)  # raises if problems; no-op if csv_path is None
    return summary


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run_validation(args.json_export, args.csv_export)
    except ValidationIssue as exc:
        print(f"Order 021 validation FAILED: {exc}", file=sys.stderr)
        return 1
    else:
        print(f"Order 021 validation PASSED: {summary.records} records validated.")
        if args.csv_export:
            print("CSV header validation passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
