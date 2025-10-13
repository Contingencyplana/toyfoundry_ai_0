"""General-purpose watcher for the High Command exchange repository."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List

STATE_FILE = Path(".toyfoundry") / "telemetry" / "exchange_watcher_state.json"


def ensure_state_dir() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict[str, float]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: Dict[str, float]) -> None:
    ensure_state_dir()
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def list_documents(path: Path) -> List[Path]:
    if not path.exists():
        return []
    return sorted(item for item in path.glob("*.json"))


def collect(exchange_root: Path, target: str | None) -> Dict[str, List[Path]]:
    pending_orders = list_documents(exchange_root / "orders" / "pending")
    pending_ack = list_documents(exchange_root / "acknowledgements" / "pending")
    inbox_reports = list_documents(exchange_root / "reports" / "inbox")

    def target_filter(paths: Iterable[Path], key: str) -> List[Path]:
        if target is None:
            return list(paths)
        filtered: List[Path] = []
        for path in paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if key == "order" and payload.get("target") == target:
                filtered.append(path)
            elif key == "ack" and payload.get("sender") == target:
                filtered.append(path)
            elif key == "report" and payload.get("origin") == target:
                filtered.append(path)
        return filtered

    return {
        "orders": target_filter(pending_orders, "order"),
        "acks": target_filter(pending_ack, "ack"),
        "reports": target_filter(inbox_reports, "report"),
    }


def snapshot(paths: Iterable[Path]) -> Dict[str, float]:
    data: Dict[str, float] = {}
    for path in paths:
        try:
            data[str(path)] = path.stat().st_mtime
        except FileNotFoundError:
            continue
    return data


def summarise(exchange_root: Path, target: str | None, state: Dict[str, float]) -> Dict[str, float]:
    collections = collect(exchange_root, target)
    combined_paths = collections["orders"] + collections["acks"] + collections["reports"]
    latest_snapshot = snapshot(combined_paths)

    new_items = [path for path in combined_paths if state.get(str(path)) != latest_snapshot.get(str(path))]
    if new_items:
        print("New exchange artefacts detected:")
        for path in new_items:
            print(f"  - {path}")
    else:
        print("No new exchange artefacts detected.")

    print("Pending orders:")
    for path in collections["orders"]:
        print(f"  - {path}")

    print("Pending acknowledgements:")
    for path in collections["acks"]:
        print(f"  - {path}")

    print("Reports awaiting review:")
    for path in collections["reports"]:
        print(f"  - {path}")

    return latest_snapshot


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch the exchange directory for new activity.")
    parser.add_argument("--exchange", type=Path, default=Path("exchange"), help="Path to the exchange repository.")
    parser.add_argument("--target", help="Filter for a specific target or origin (orders, acks, reports).")
    parser.add_argument("--watch", action="store_true", help="Continuously watch the exchange tree.")
    parser.add_argument("--interval", type=float, default=30.0, help="Polling interval when --watch is set.")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    exchange_root = args.exchange
    if not exchange_root.exists():
        print(f"Exchange directory not found: {exchange_root}", file=sys.stderr)
        return 1

    ensure_state_dir()
    state = load_state()

    if args.watch:
        try:
            while True:
                state = summarise(exchange_root, args.target, state)
                save_state(state)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopping exchange watcher.")
            return 0
    else:
        state = summarise(exchange_root, args.target, state)
        save_state(state)
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))