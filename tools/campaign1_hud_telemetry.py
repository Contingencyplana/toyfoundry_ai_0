"""Compute HUD telemetry metrics for Campaign 1 playtests (TTF, revive cadence, one-more-run)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _load_record(log_path: Path) -> Dict[str, Any]:
    text = log_path.read_text(encoding="utf-8").strip()
    line = text.splitlines()[0]
    return json.loads(line)


def _first(events: Iterable[Dict[str, Any]], event_type: str) -> Optional[Dict[str, Any]]:
    for ev in events:
        if ev.get("type") == event_type:
            return ev
    return None


def _last_before(events: List[Dict[str, Any]], event_type: str, before: datetime) -> Optional[Dict[str, Any]]:
    chosen: Optional[Dict[str, Any]] = None
    for ev in events:
        if ev.get("type") != event_type:
            continue
        ts = ev.get("t")
        if not isinstance(ts, str):
            continue
        t = _parse_iso(ts)
        if t < before:
            chosen = ev
    return chosen


def _emoji_only(value: str) -> bool:
    # Very loose check: require at least one non-ASCII char and no alphanumerics.
    return any(ord(ch) > 127 for ch in value) and all(not ch.isalnum() for ch in value if ch.strip())


def compute_metrics(record: Dict[str, Any]) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = record.get("events") or []

    role_lock = _first(events, "role_lock")
    ability_cast = _first(events, "ability_cast")
    extraction = _first(events, "extraction")
    revive = _first(events, "revive")
    one_more = _first(events, "one_more_prompt")

    def delta_ms(a: Dict[str, Any], b: Dict[str, Any]) -> int:
        return int((_parse_iso(a["t"]) - _parse_iso(b["t"])).total_seconds() * 1000)

    time_to_fun_ms = delta_ms(ability_cast, role_lock) if role_lock and ability_cast else None
    extraction_ms = delta_ms(extraction, role_lock) if role_lock and extraction else None

    revive_ms = None
    if revive:
        revive_time = _parse_iso(revive["t"])
        downed = _last_before(events, "downed", before=revive_time)
        if downed:
            revive_ms = int((revive_time - _parse_iso(downed["t"])).total_seconds() * 1000)

    one_more_accept = one_more.get("accepted") if isinstance(one_more, dict) else None

    non_emoji_inputs: List[Dict[str, Any]] = []
    for ev in events:
        for key in ("emoji", "by"):
            val = ev.get(key)
            if isinstance(val, str) and val.strip() and not _emoji_only(val):
                non_emoji_inputs.append({"type": ev.get("type"), "field": key, "value": val})

    return {
        "schema": "toyfoundry-campaign1-hud@1.0",
        "order_id": record.get("order_id"),
        "workspace": record.get("workspace"),
        "run_id": record.get("run_id"),
        "metrics": {
            "time_to_fun_ms": time_to_fun_ms,
            "revive_ms": revive_ms,
            "extraction_ms": extraction_ms,
            "one_more_accept": one_more_accept,
        },
        "events_count": len(events),
        "guardrails": {
            "input_mode": "emoji_dsl_only",
            "non_emoji_inputs": non_emoji_inputs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute HUD telemetry metrics from Campaign 1 playtest logs")
    parser.add_argument("log_path", type=Path, help="Path to JSON/JSONL playtest log (from campaign1_playtest_stub)")
    parser.add_argument(
        "--output",
        default="logs/order-2025-11-23-060-m1-hud-telemetry.json",
        help="Output JSON file for computed HUD metrics",
    )
    args = parser.parse_args()

    record = _load_record(args.log_path)
    report = compute_metrics(record)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] HUD telemetry written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
