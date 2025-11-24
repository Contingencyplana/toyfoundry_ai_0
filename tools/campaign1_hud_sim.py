"""Simulate a thin HUD playtest for Campaign 1 and emit emoji-DSL events + HUD metrics."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


def _now() -> datetime:
    return datetime.now(timezone.utc)


def simulate_run(
    *,
    ttf_ms: int,
    revive_ms: int,
    extraction_ms: int,
    one_more_accept: bool,
    run_id: str,
) -> Dict[str, Any]:
    start = _now()
    events: List[Dict[str, Any]] = []

    def stamp(delta_ms: int) -> str:
        return (start + timedelta(milliseconds=delta_ms)).isoformat()

    events.append({"t": stamp(0), "type": "role_lock", "player": "P1", "emoji": "🛡️"})
    events.append({"t": stamp(0), "type": "role_lock", "player": "P2", "emoji": "✨"})
    events.append({"t": stamp(ttf_ms), "type": "ability_cast", "player": "P1", "emoji": "🛡️✨"})
    events.append({"t": stamp(ttf_ms), "type": "ability_cast", "player": "P2", "emoji": "✨🌑"})
    events.append({"t": stamp(extraction_ms - 50000), "type": "downed", "player": "P2", "by": "👻"})
    events.append({"t": stamp(extraction_ms - 50000 + revive_ms), "type": "revive", "player": "P2", "by": "P1", "emoji": "🛡️✨"})
    events.append({"t": stamp(extraction_ms), "type": "extraction", "result": "success"})
    events.append({"t": stamp(extraction_ms + 5000), "type": "one_more_prompt", "accepted": bool(one_more_accept)})

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
                "time_to_fun_ms": ttf_ms,
                "revive_ms": revive_ms,
                "one_more_accept": one_more_accept,
            },
            "guardrails": {
                "input_mode": "emoji_dsl_only",
                "filters": ["no free text", "template-bound commands"],
            },
        },
        "metrics": {
            "time_to_fun_ms": ttf_ms,
            "revive_ms": revive_ms,
            "extraction_ms": extraction_ms,
            "one_more_accept": one_more_accept,
        },
        "events": events,
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate a thin HUD playtest for Campaign 1 (emoji DSL only).")
    parser.add_argument("--output", default="logs/order-2025-11-23-060-m1-ui-playtest.jsonl", help="Output JSONL path")
    parser.add_argument("--run-id", default=None, help="Run identifier (defaults to timestamped ID)")
    parser.add_argument("--ttf-ms", type=int, default=3200, help="Time-to-Fun in milliseconds (role lock -> first ability)")
    parser.add_argument("--revive-ms", type=int, default=15000, help="Down -> revive delta in milliseconds")
    parser.add_argument("--extraction-ms", type=int, default=140000, help="Role lock -> extraction delta in milliseconds")
    parser.add_argument("--one-more-accept", action="store_true", help="Mark one-more-run prompt accepted (default False)")
    args = parser.parse_args()

    run_id = args.run_id or f"campaign1-m1-{_now().strftime('%Y%m%dT%H%M%SZ')}"
    record = simulate_run(
        ttf_ms=args.ttf_ms,
        revive_ms=args.revive_ms,
        extraction_ms=args.extraction_ms,
        one_more_accept=bool(args.one_more_accept),
        run_id=run_id,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Thin HUD playtest log written to {out_path} (run_id={run_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
