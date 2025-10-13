"""Shared logging utilities for Toyfoundry Forge rituals."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

TELEMETRY_DIR = Path(".toyfoundry") / "telemetry"
RITUAL_LOG = TELEMETRY_DIR / "forge_rituals.jsonl"


def timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def log_ritual_event(ritual: str, status: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Append a ritual telemetry entry and return the logged payload."""
    entry = {
        "timestamp": timestamp(),
        "ritual": ritual,
        "status": status,
        "metadata": metadata,
    }
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    with RITUAL_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry))
        handle.write("\n")
    return entry