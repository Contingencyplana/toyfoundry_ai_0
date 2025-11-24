"""Emit a stub Campaign 1 M1 playtest log with thin HUD metrics routed through emoji DSL."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_stub_run(run_id: str) -> Dict[str, Any]:
    start = _now_utc()
    first_ability = start + timedelta(seconds=3.2)
    downed = start + timedelta(seconds=90)
    revived = downed + timedelta(seconds=15)
    extraction = start + timedelta(seconds=140)
    one_more_prompt = extraction + timedelta(seconds=5)

    events: List[Dict[str, Any]] = [
        {"t": start.isoformat(), "type": "role_lock", "player": "P1", "emoji": "🛡️"},
        {"t": start.isoformat(), "type": "role_lock", "player": "P2", "emoji": "✨"},
        {"t": first_ability.isoformat(), "type": "ability_cast", "player": "P1", "emoji": "🛡️✨"},
        {"t": first_ability.isoformat(), "type": "ability_cast", "player": "P2", "emoji": "✨🌑"},
        {"t": downed.isoformat(), "type": "downed", "player": "P2", "by": "👻"},
        {"t": revived.isoformat(), "type": "revive", "player": "P2", "by": "P1", "emoji": "🛡️✨"},
        {"t": extraction.isoformat(), "type": "extraction", "result": "success"},
        {"t": one_more_prompt.isoformat(), "type": "one_more_prompt", "accepted": True},
    ]

    metrics = {
        "time_to_fun_ms": int((first_ability - start).total_seconds() * 1000),
        "revive_ms": int((revived - downed).total_seconds() * 1000),
        "extraction_ms": int((extraction - start).total_seconds() * 1000),
        "one_more_accept": True,
    }

    record: Dict[str, Any] = {
        "schema": "toyfoundry-campaign1-m1@1.0",
        "order_id": "order-2025-11-23-060",
        "workspace": "toyfoundry_ai_0",
        "run_id": run_id,
        "timestamp": start.isoformat(),
        "session": {
            "players": ["P1", "P2"],
            "roles": {"P1": "🛡️", "P2": "✨"},
            "enemies": ["👻", "💀"],
            "hud": {
                "time_to_fun_ms": metrics["time_to_fun_ms"],
                "revive_ms": metrics["revive_ms"],
                "one_more_accept": metrics["one_more_accept"],
            },
            "guardrails": {
                "input_mode": "emoji_dsl_only",
                "filters": ["no free text", "template-bound commands"],
            },
        },
        "metrics": metrics,
        "events": events,
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit stub Campaign 1 playtest log")
    parser.add_argument(
        "--output",
        default="logs/order-2025-11-23-060-m1-playtest.jsonl",
        help="Path for the generated JSONL log",
    )
    parser.add_argument(
        "--run-id",
        default=lambda: f"campaign1-m1-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        help="Run identifier (defaults to timestamped ID)",
    )
    args = parser.parse_args()

    run_id = args.run_id() if callable(args.run_id) else args.run_id
    record = build_stub_run(run_id)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Wrote stub playtest log to {out_path} with run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
