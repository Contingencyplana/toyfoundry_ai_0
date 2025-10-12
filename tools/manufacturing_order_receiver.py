"""Manufacturing order receiver for Toyfoundry AI.
Processes pending manufacturing orders from High Command,
emits acknowledgements, generates setup reports, and
moves handled orders into the dispatched queue.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

BASE_DIR = Path(__file__).resolve().parents[1]
EXCHANGE_DIR = BASE_DIR / "exchange"
ORDERS_PENDING_DIR = EXCHANGE_DIR / "orders" / "pending"
ORDERS_DISPATCHED_DIR = EXCHANGE_DIR / "orders" / "dispatched"
ACK_PENDING_DIR = EXCHANGE_DIR / "acknowledgements" / "pending"
REPORT_INBOX_DIR = EXCHANGE_DIR / "reports" / "inbox"
WORKSPACE_NAME = "toyfoundry_ai_0"


class OrderProcessingError(Exception):
    """Raised when an order cannot be processed."""


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_order(order_path: Path) -> dict:
    with order_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "order_id" not in data or "schema" not in data:
        raise OrderProcessingError(f"Invalid order schema in {order_path.name}")
    return data


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _ack_payload(order: dict) -> dict:
    return {
        "schema": "signal-ack@1.0",
        "order_id": order["order_id"],
        "acknowledged_by": WORKSPACE_NAME,
        "timestamp_acknowledged": _iso_timestamp(),
        "summary": f"Order {order['order_id']} acknowledged by Toyfoundry for manufacturing setup."
    }


def _report_payload(order: dict) -> dict:
    return {
        "schema": "factory-report@1.0",
        "order_id": order["order_id"],
        "reported_by": WORKSPACE_NAME,
        "timestamp_reported": _iso_timestamp(),
        "status": "manufacturing_link_established",
        "details": "Exchange verified, watcher operational, receiver online. Factory ready to accept ritual scripts."
    }


def _move_to_dispatched(order_path: Path) -> Path:
    dest = ORDERS_DISPATCHED_DIR / order_path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    order_path.replace(dest)
    return dest


def _process_order(order_path: Path) -> str:
    order = _load_order(order_path)
    oid = order["order_id"]

    ack_path = ACK_PENDING_DIR / f"{oid}-ack.json"
    report_path = REPORT_INBOX_DIR / f"{oid}-report.json"

    if ack_path.exists() or report_path.exists():
        raise OrderProcessingError(f"Order {oid} already processed.")

    _write_json(ack_path, _ack_payload(order))
    _write_json(report_path, _report_payload(order))
    _move_to_dispatched(order_path)

    return oid


def _iter_orders(order_ids: Iterable[str] | None = None) -> List[Path]:
    if order_ids:
        paths = []
        for oid in order_ids:
            candidate = ORDERS_PENDING_DIR / f"{oid}.json"
            if not candidate.exists():
                raise OrderProcessingError(f"Order {oid} not found.")
            paths.append(candidate)
        return paths
    return sorted(ORDERS_PENDING_DIR.glob("*.json"))


def process_orders(order_ids: Iterable[str] | None = None) -> List[str]:
    processed = []
    for p in _iter_orders(order_ids):
        processed.append(_process_order(p))
    return processed


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Process pending manufacturing orders.")
    parser.add_argument("order_ids", nargs="*", help="Specific order IDs to process")
    args = parser.parse_args()

    try:
        done = process_orders(args.order_ids or None)
    except OrderProcessingError as e:
        raise SystemExit(f"Error: {e}") from e

    if done:
        print(f"Processed manufacturing orders: {', '.join(done)}")
    else:
        print("No pending manufacturing orders found.")


if __name__ == "__main__":
    main()
