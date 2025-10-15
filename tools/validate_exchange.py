import json
import sys
from pathlib import Path


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load {path}: {e}")
        return None


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    exchange_dir = repo_root / "exchange"
    ledger_path = exchange_dir / "ledger" / "index.json"

    problems = 0

    if not ledger_path.exists():
        print(f"ERROR: Ledger not found: {ledger_path}")
        return 2

    ledger = load_json(ledger_path)
    if ledger is None:
        return 3

    orders = ledger.get("orders", {})
    acks_map = ledger.get("acks", {})
    reports_map = ledger.get("reports", {})

    # 1) Cross-check paths exist on disk and are consistent across sections
    def check_path(kind: str, order_id: str, rel_path: str):
        nonlocal problems
        if not isinstance(rel_path, str) or not rel_path:
            print(f"ERROR: {kind} path missing for {order_id}")
            problems += 1
            return
        p = exchange_dir / rel_path
        if not p.exists():
            print(f"ERROR: {kind} path does not exist for {order_id}: {rel_path}")
            problems += 1

    # a) orders.* ack_path/report_path existence
    for oid, meta in orders.items():
        ack_rel = meta.get("ack_path")
        rep_rel = meta.get("report_path")
        if ack_rel:
            check_path("ack", oid, ack_rel)
        if rep_rel:
            check_path("report", oid, rep_rel)

        # b) consistency with acks/reports maps
        ack_key = f"{oid}-ack" if not oid.endswith("-ack") else oid
        rep_key = f"{oid}-report" if not oid.endswith("-report") else oid
        am_rel = acks_map.get(ack_key)
        rm_rel = reports_map.get(rep_key)
        if ack_rel and am_rel and ack_rel != am_rel:
            print(f"ERROR: ack path mismatch for {oid}: orders={ack_rel} vs acks={am_rel}")
            problems += 1
        if rep_rel and rm_rel and rep_rel != rm_rel:
            print(f"ERROR: report path mismatch for {oid}: orders={rep_rel} vs reports={rm_rel}")
            problems += 1

    # 2) Guardrail: ensure no files were added under orders/dispatched without ledger entries
    dispatched_dir = exchange_dir / "orders" / "dispatched"
    if dispatched_dir.exists():
        for f in dispatched_dir.glob("order-*-*.json"):
            oid = f.stem  # e.g., order-2025-...-NNN
            if oid not in orders:
                print(f"ERROR: dispatched file without ledger entry: {f.name}")
                problems += 1

    if problems == 0:
        print("OK: exchange ledger and filesystem are consistent.")
        return 0
    else:
        print(f"FAIL: Found {problems} problem(s).")
        return 1


if __name__ == "__main__":
    sys.exit(main())

