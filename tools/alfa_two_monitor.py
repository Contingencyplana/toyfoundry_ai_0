"""Monitoring hooks for Toyfoundry Alfa Two factory-order emissions."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableSet, Sequence

FACTORY_SCHEMA = "factory-order@1.0"
DEFAULT_ORDERS_DIR = Path("exchange/orders/outbox/emoji_runtime")
DEFAULT_TELEMETRY_DIR = Path("telemetry/alfa_two/live")
STATE_FILENAME = "_processed.json"
NARRATOR_METRICS_PATH = Path("monitoring/logs/narrator_metrics.json")
GLYPH_LOG_PATH = Path("monitoring/logs/glyph_vo_discrepancies.log")


@dataclass
class MonitoringConfig:
    orders_dir: Path
    telemetry_dir: Path
    narrator_metrics: Path
    glyph_log: Path
    once: bool
    interval: float


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor Alfa Two factory-order emissions for telemetry output")
    parser.add_argument(
        "--orders-dir",
        type=Path,
        default=DEFAULT_ORDERS_DIR,
        help="Directory containing emitted factory-order@1.0 documents.",
    )
    parser.add_argument(
        "--telemetry-dir",
        type=Path,
        default=DEFAULT_TELEMETRY_DIR,
        help="Directory where telemetry snapshots will be written.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Polling interval (seconds) when running continuously.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process available orders one time and exit.",
    )
    return parser.parse_args(argv)


def load_state(state_path: Path) -> MutableSet[str]:
    if not state_path.exists():
        return set()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    processed = data.get("order_ids")
    if not isinstance(processed, list):
        return set()
    return {item for item in processed if isinstance(item, str)}


def save_state(state_path: Path, order_ids: Sequence[str]) -> None:
    payload = {
        "order_ids": list(order_ids),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_payload(path: Path) -> Mapping[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != FACTORY_SCHEMA:
        raise ValueError(f"Unsupported schema in {path}: {data.get('schema')}")
    return data


def hash_payload(data: Mapping[str, object]) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_telemetry_snapshot(telemetry_dir: Path, order_id: str, data: Mapping[str, object], checksum: str) -> None:
    snapshot = {
        "order_id": order_id,
        "checksum_sha256": checksum,
        "glyph_count": len(data.get("glyph_chain", [])),
        "telemetry_status": (data.get("telemetry_stub") or {}).get("status"),
        "summary": data.get("summary"),
        "narration_line": (data.get("narration") or {}).get("line"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    destination = telemetry_dir / f"{order_id}.json"
    destination.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


def append_narrator_metrics(path: Path, order_id: str, data: Mapping[str, object], checksum: str) -> None:
    metrics_entry = {
        "order_id": order_id,
        "checksum_sha256": checksum,
        "summary": data.get("summary"),
        "narration_line": (data.get("narration") or {}).get("line"),
        "beats": (data.get("narration") or {}).get("beats"),
        "glyph_count": len(data.get("glyph_chain", [])),
        "telemetry_status": (data.get("telemetry_stub") or {}).get("status"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []
    existing.append(metrics_entry)
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")


def log_discrepancies(path: Path, order_id: str, data: Mapping[str, object]) -> None:
    narration = data.get("narration") or {}
    summary = data.get("summary")
    line = narration.get("line") if isinstance(narration, Mapping) else None
    if line != summary:
        message = (
            f"[{datetime.now(timezone.utc).isoformat()}] order_id={order_id} "
            f"summary/narration mismatch: summary={summary!r} narration_line={line!r}\n"
        )
        path.write_text((path.read_text(encoding="utf-8") if path.exists() else "") + message, encoding="utf-8")


def process_orders(config: MonitoringConfig) -> bool:
    ensure_dirs(config.telemetry_dir, config.narrator_metrics.parent, config.glyph_log.parent)
    config.glyph_log.touch(exist_ok=True)
    state_path = config.telemetry_dir / STATE_FILENAME
    processed = load_state(state_path)
    updated = False

    order_files = sorted(config.orders_dir.glob("*.json"))
    for order_path in order_files:
        try:
            payload = load_payload(order_path)
        except ValueError as exc:
            print(f"Skipping {order_path}: {exc}")
            continue
        order_id = str(payload.get("order_id"))
        if not order_id or order_id in processed:
            continue

        checksum = hash_payload(payload)
        write_telemetry_snapshot(config.telemetry_dir, order_id, payload, checksum)
        append_narrator_metrics(config.narrator_metrics, order_id, payload, checksum)
        log_discrepancies(config.glyph_log, order_id, payload)
        processed.add(order_id)
        updated = True
        print(f"Processed {order_id}")

    if updated:
        save_state(state_path, sorted(processed))
    return updated


def run(config: MonitoringConfig) -> None:
    if config.once:
        process_orders(config)
        return

    while True:
        process_orders(config)
        time.sleep(config.interval)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    config = MonitoringConfig(
        orders_dir=args.orders_dir,
        telemetry_dir=args.telemetry_dir,
        narrator_metrics=NARRATOR_METRICS_PATH,
        glyph_log=GLYPH_LOG_PATH,
        once=args.once,
        interval=args.interval,
    )

    if not config.orders_dir.exists():
        print(f"Orders directory does not exist: {config.orders_dir}")
        return 1

    run(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
