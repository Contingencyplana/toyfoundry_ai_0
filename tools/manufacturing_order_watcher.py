"""Toyfoundry manufacturing order watcher.

Scans the exchange repository for orders targeting Toyfoundry and reports
outstanding acknowledgements or reports so the factory stays in sync with
High Command.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from tools.forge.forge_mint_alfa import TELEMETRY_FILE  # type: ignore

STATE_ROOT = Path(".toyfoundry")
STATE_FILE = STATE_ROOT / "manufacturing_order_watcher_state.json"


def load_state() -> Dict[str, float]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(snapshot: Dict[str, float]) -> None:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")


def discover_order_files(exchange_root: Path) -> Iterable[Path]:
    pending_dir = exchange_root / "orders" / "pending"
    if not pending_dir.exists():
        return []
    return sorted(path for path in pending_dir.glob("*.json"))


def load_json(document: Path) -> Dict:
    try:
        return json.loads(document.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse {document}: {exc}") from exc


def filter_orders(order_paths: Iterable[Path], target: str) -> List[Tuple[Path, Dict]]:
    matching: List[Tuple[Path, Dict]] = []
    for path in order_paths:
        payload = load_json(path)
        if payload.get("target") == target:
            matching.append((path, payload))
    return matching


def discover_pending_acks(exchange_root: Path, target: str) -> List[Path]:
    pending_dir = exchange_root / "acknowledgements" / "pending"
    if not pending_dir.exists():
        return []
    matches: List[Path] = []
    for path in pending_dir.glob("*.json"):
        payload = load_json(path)
        if payload.get("sender") == target:
            matches.append(path)
    return sorted(matches)


def discover_inbox_reports(exchange_root: Path, target: str) -> List[Path]:
    inbox_dir = exchange_root / "reports" / "inbox"
    if not inbox_dir.exists():
        return []
    matches: List[Path] = []
    for path in inbox_dir.glob("*.json"):
        payload = load_json(path)
        if payload.get("origin") == target:
            matches.append(path)
    return sorted(matches)


def build_snapshot(order_paths: Iterable[Path]) -> Dict[str, float]:
    snapshot: Dict[str, float] = {}
    for path in order_paths:
        try:
            snapshot[path.name] = path.stat().st_mtime
        except FileNotFoundError:
            continue
    return snapshot


def summarise_orders(orders: List[Tuple[Path, Dict]]) -> None:
    if not orders:
        print("No manufacturing orders pending.")
        return
    print("Manufacturing orders pending:")
    for path, payload in orders:
        order_id = payload.get("order_id", path.name)
        summary = payload.get("summary", "(no summary)")
        priority = payload.get("priority", "standard")
        print(f"  - {order_id} | priority={priority} | {summary}")
        directives = payload.get("directives", [])
        for directive in directives:
            action = directive.get("action", "(no action)")
            details = directive.get("details", "")
            action_lower = action.lower()
            details_lower = details.lower()
            if "mint" in action_lower or "forge" in action_lower:
                print("      · Ritual cue: python -m tools.forge.forge_mint_alfa --name <alfa-name> --dry-run")
                print(f"      · Details: {details}")
                print(f"      · Telemetry: {TELEMETRY_FILE}")
            elif "quilt" in action_lower or "quilt" in details_lower:
                print("      · Loom cue: python -m tools.telemetry.quilt_loom")
                print(f"      · Details: {details}")
                print("      · Output: .toyfoundry/telemetry/quilt/quilt_rollup.json")
            else:
                print(f"      · {action}: {details}")


def summarise_paths(title: str, paths: List[Path]) -> None:
    if not paths:
        print(f"No {title}.")
        return
    print(f"{title}:")
    for path in paths:
        print(f"  - {path}")


def run_once(exchange_root: Path, target: str, state: Dict[str, float]) -> Dict[str, float]:
    order_paths = list(discover_order_files(exchange_root))
    orders = filter_orders(order_paths, target)
    snapshot = build_snapshot(order_paths)

    new_orders = [item for item in orders if state.get(item[0].name) != snapshot.get(item[0].name)]

    if new_orders:
        print("New or updated Toyfoundry orders detected.")
    summarise_orders(orders)

    pending_acks = discover_pending_acks(exchange_root, target)
    summarise_paths("Acknowledgements awaiting dispatch", pending_acks)

    inbox_reports = discover_inbox_reports(exchange_root, target)
    summarise_paths("Reports awaiting review by High Command", inbox_reports)

    return snapshot


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch exchange orders for Toyfoundry manufacturing directives.")
    parser.add_argument("--exchange", type=Path, default=Path("exchange"), help="Path to the exchange repository.")
    parser.add_argument("--target", default="toyfoundry_ai_0", help="Order target identifier to filter for.")
    parser.add_argument("--watch", action="store_true", help="Continuously watch for new orders.")
    parser.add_argument("--interval", type=float, default=30.0, help="Polling interval in seconds when --watch is set.")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    exchange_root = args.exchange
    if not exchange_root.exists():
        print(f"Exchange directory not found: {exchange_root}", file=sys.stderr)
        return 1

    state = load_state()

    if args.watch:
        print(f"Watching {exchange_root} for Toyfoundry orders targeting {args.target} (interval {args.interval}s)...")
        try:
            while True:
                state = run_once(exchange_root, args.target, state)
                save_state(state)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopping watcher.")
            return 0
    else:
        state = run_once(exchange_root, args.target, state)
        save_state(state)
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
