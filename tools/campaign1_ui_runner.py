"""Minimal thin-UI runner for Campaign 1: emits emoji-DSL events + HUD metrics."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_EVENTS = [
    {"offset_ms": 0, "type": "role_lock", "player": "P1", "emoji": "🛡️"},
    {"offset_ms": 0, "type": "role_lock", "player": "P2", "emoji": "✨"},
    {"offset_ms": 3200, "type": "ability_cast", "player": "P1", "emoji": "🛡️✨"},
    {"offset_ms": 3200, "type": "ability_cast", "player": "P2", "emoji": "✨🌑"},
    {"offset_ms": 90000, "type": "downed", "player": "P2", "by": "👻"},
    {"offset_ms": 105000, "type": "revive", "player": "P2", "by": "P1", "emoji": "🛡️✨"},
    {"offset_ms": 140000, "type": "extraction", "result": "success"},
    {"offset_ms": 145000, "type": "one_more_prompt", "accepted": True},
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_script(path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            evt = json.loads(line)
            if "offset_ms" in evt and "type" in evt:
                events.append(evt)
        except json.JSONDecodeError:
            continue
    return events


def _emoji_only(value: str) -> bool:
    return any(ord(ch) > 127 for ch in value) and all(not ch.isalnum() for ch in value if ch.strip())


def build_run(events: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
    start = _now()
    normalized: List[Dict[str, Any]] = []
    for raw in events:
        offset_ms = int(raw.get("offset_ms", 0))
        evt = dict(raw)
        evt["t"] = (start + timedelta(milliseconds=offset_ms)).isoformat()
        evt.pop("offset_ms", None)
        normalized.append(evt)

    role_lock = next((e for e in normalized if e.get("type") == "role_lock"), None)
    ability_cast = next((e for e in normalized if e.get("type") == "ability_cast"), None)
    extraction = next((e for e in normalized if e.get("type") == "extraction"), None)

    def delta_ms(a: Optional[Dict[str, Any]], b: Optional[Dict[str, Any]]) -> Optional[int]:
        if not a or not b:
            return None
        return int(
            (
                datetime.fromisoformat(a["t"])
                - datetime.fromisoformat(b["t"])
            ).total_seconds()
            * 1000
        )

    time_to_fun_ms = delta_ms(ability_cast, role_lock)
    extraction_ms = delta_ms(extraction, role_lock)

    revive_ms = None
    revive = next((e for e in normalized if e.get("type") == "revive"), None)
    if revive:
        revive_time = datetime.fromisoformat(revive["t"])
        down = None
        for e in normalized:
            if e.get("type") == "downed":
                if datetime.fromisoformat(e["t"]) < revive_time:
                    down = e
        if down:
            revive_ms = int((revive_time - datetime.fromisoformat(down["t"])).total_seconds() * 1000)

    one_more = next((e for e in normalized if e.get("type") == "one_more_prompt"), None)
    one_more_accept = one_more.get("accepted") if isinstance(one_more, dict) else None

    non_emoji: List[Dict[str, Any]] = []
    for ev in normalized:
        for key in ("emoji", "by"):
            val = ev.get(key)
            if isinstance(val, str) and val.strip() and not _emoji_only(val):
                non_emoji.append({"type": ev.get("type"), "field": key, "value": val})

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
                "time_to_fun_ms": time_to_fun_ms,
                "revive_ms": revive_ms,
                "one_more_accept": one_more_accept,
            },
            "guardrails": {
                "input_mode": "emoji_dsl_only",
                "filters": ["no free text", "template-bound commands"],
                "non_emoji_inputs": non_emoji,
            },
        },
        "metrics": {
            "time_to_fun_ms": time_to_fun_ms,
            "revive_ms": revive_ms,
            "extraction_ms": extraction_ms,
            "one_more_accept": one_more_accept,
        },
        "events": normalized,
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Thin HUD runner (emoji-DSL only) for Campaign 1 playtests.")
    parser.add_argument("--output", default="logs/order-2025-11-23-060-m1-ui-live.jsonl", help="Output JSONL path")
    parser.add_argument("--run-id", default=None, help="Run identifier (defaults to timestamped ID)")
    parser.add_argument("--script", type=Path, help="Optional JSONL script of events with offset_ms and fields")
    args = parser.parse_args()

    events = DEFAULT_EVENTS
    if args.script:
        parsed = _parse_script(args.script)
        if parsed:
            events = parsed

    run_id = args.run_id or f"campaign1-m1-{_now().strftime('%Y%m%dT%H%M%SZ')}"
    record = build_run(events, run_id)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Thin UI run written to {out_path} (run_id={run_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
