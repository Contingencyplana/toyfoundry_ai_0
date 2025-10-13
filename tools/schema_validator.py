"""Lightweight validator for High Command exchange payloads."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

SCHEMA_REQUIREMENTS: Dict[str, List[str]] = {
    "high-command-order@1.0": [
        "order_id",
        "target",
        "directives",
        "timestamp_issued",
    ],
    "signal-ack@1.0": [
        "ack_id",
        "referenced_id",
        "sender",
        "receiver",
        "status",
    ],
    "field-report@1.0": [
        "report_id",
        "origin",
        "relates_to",
        "status",
    ],
    "factory-report@1.0": [
        "order_id",
        "reported_by",
        "timestamp_reported",
        "status",
    ],
}


class ValidationError(RuntimeError):
    """Raised when a document fails validation."""


def validate_document(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema")
    if not schema:
        raise ValidationError(f"{path}: missing 'schema' field")

    required_fields = SCHEMA_REQUIREMENTS.get(schema)
    if required_fields is None:
        raise ValidationError(f"{path}: unknown schema '{schema}'")

    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValidationError(f"{path}: missing required keys {missing}")

    if schema == "high-command-order@1.0" and not isinstance(data.get("directives"), list):
        raise ValidationError(f"{path}: directives must be a list")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate exchange payloads against baseline requirements.")
    parser.add_argument("paths", nargs="+", type=Path, help="One or more JSON documents to validate.")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    errors = 0
    for path in args.paths:
        try:
            validate_document(path)
        except (OSError, ValidationError, json.JSONDecodeError) as exc:
            errors += 1
            print(f"Validation failed: {exc}", file=sys.stderr)
        else:
            print(f"Validation passed: {path}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
