"""Tests for promoting emoji-runtime payloads into factory-order documents."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.emoji_runtime_promoter import (
    EmojiRuntimeValidationError,
    build_factory_order_from_emoji,
    load_emoji_runtime_payload,
)
from tools.factory_order_emitter import PayloadValidationError, write_factory_order

FIXTURES = Path(__file__).parent


def fixture_path(name: str) -> Path:
    return FIXTURES / name


def test_build_factory_order_preserves_metadata(tmp_path: Path) -> None:
    payload = load_emoji_runtime_payload(fixture_path("sample_forge_payload.json"))
    factory_order = build_factory_order_from_emoji(
        payload,
        order_id="TF-EMOJI-01",
        issued_by="toyfoundry_ai_0",
        target="toyfoundry_ai_0",
        priority="standard",
        timestamp_issued="2025-11-01T10:15:00Z",
        narrator="war-office-storyteller",
    )

    assert factory_order["schema"] == "factory-order@1.0"
    assert factory_order["glyph_chain"] == ["🛠️", "⚒️", "🛡️", "🤖"]
    assert factory_order["metadata"]["emoji_runtime_schema"] == "emoji-runtime@1.0"
    assert factory_order["metadata"]["emoji_runtime_template"] == "basic_ritual_forge"
    assert factory_order["metadata"]["emoji_runtime_timestamp"] == "2025-11-01T10:05:00Z"
    assert factory_order["directives"] == [
        {"type": "glyph", "value": "🛠️"},
        {"type": "glyph", "value": "⚒️"},
        {"type": "glyph", "value": "🛡️"},
        {"type": "glyph", "value": "🤖"},
    ]

    destination = tmp_path / "TF-EMOJI-01.json"
    write_factory_order(factory_order, destination)
    written = json.loads(destination.read_text())
    assert written["order_id"] == "TF-EMOJI-01"


def test_secondary_outcomes_captured_in_metadata() -> None:
    payload = load_emoji_runtime_payload(fixture_path("sample_conditional_repeat_payload.json"))
    factory_order = build_factory_order_from_emoji(
        payload,
        order_id="TF-EMOJI-02",
        issued_by="toyfoundry_ai_0",
        target="toyfoundry_ai_0",
        priority="urgent",
        timestamp_issued="2025-11-01T10:20:00Z",
    )

    assert factory_order["metadata"]["emoji_runtime_outcomes"] == ["victory", "fallback_signal"]
    assert factory_order["telemetry_stub"]["status"] == "warning"
    assert factory_order["summary"] == "Scout tests the barrier, then signals fallback support."


def test_invalid_schema_raises(tmp_path: Path) -> None:
    source = fixture_path("sample_forge_payload.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    data["schema"] = "emoji-runtime@0.9"
    invalid_payload = tmp_path / "invalid_payload.json"
    invalid_payload.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(EmojiRuntimeValidationError):
        load_emoji_runtime_payload(invalid_payload)


def test_summary_alignment_mismatch_raises() -> None:
    payload = load_emoji_runtime_payload(fixture_path("sample_forge_payload.json"))
    with pytest.raises(PayloadValidationError):
        build_factory_order_from_emoji(
            payload,
            order_id="TF-EMOJI-MISMATCH",
            issued_by="toyfoundry_ai_0",
            target="toyfoundry_ai_0",
            priority="standard",
            timestamp_issued="2025-11-01T10:30:00Z",
            summary_override="Different lore line",
        )
