"""Tests for the Toyfoundry Alfa Two factory-order emission path."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

factory_order_emitter = import_module("tools.factory_order_emitter")
PayloadValidationError = factory_order_emitter.PayloadValidationError
build_factory_order = factory_order_emitter.build_factory_order
load_translator_payload = factory_order_emitter.load_translator_payload
write_factory_order = factory_order_emitter.write_factory_order


FIXTURES_DIR = Path(__file__).parent


def _sample_path(name: str) -> Path:
    return FIXTURES_DIR / name


def test_build_factory_order_from_sample(tmp_path: Path) -> None:
    translator = load_translator_payload(_sample_path("sample_translator_payload.json"))
    order_id = "TF-ALFA2-TEST-00"
    payload = build_factory_order(
        translator,
        order_id=order_id,
        issued_by="toyfoundry_ai_0",
        target="forge",
        priority="standard",
        timestamp_issued="2025-10-29T00:00:00Z",
        summary_override=None,
        narrator="war-office-persona",
        extra_fields={"attachments": []},
    )
    destination = tmp_path / f"{order_id}.json"
    write_factory_order(payload, destination)

    emitted = json.loads(destination.read_text())
    assert emitted["order_id"] == order_id
    assert emitted["schema"] == "factory-order@1.0"
    assert emitted["metadata"]["narrator_profile"] == "war-office-persona"
    assert emitted["glyph_chain"] == translator.glyph_chain


def test_summary_override_mismatch_raises() -> None:
    translator = load_translator_payload(_sample_path("sample_translator_payload.json"))

    with pytest.raises(PayloadValidationError):
        build_factory_order(
            translator,
            order_id="TF-ALFA2-TEST-01",
            issued_by="toyfoundry_ai_0",
            target="forge",
            priority="standard",
            timestamp_issued=datetime.now(timezone.utc).isoformat(),
            summary_override="Different lore summary",
            narrator=None,
            extra_fields=None,
        )


def test_missing_units_processed_rejected() -> None:
    with pytest.raises(PayloadValidationError) as exc_info:
        load_translator_payload(_sample_path("sample_translator_payload_missing_units.json"))

    assert "telemetry_stub missing 'units_processed'" in str(exc_info.value)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "sample_translator_payload.json",
        "sample_translator_payload_scout.json",
    ],
)
def test_all_fixture_payloads_emit_without_error(fixture_name: str) -> None:
    translator = load_translator_payload(_sample_path(fixture_name))
    payload = build_factory_order(
        translator,
        order_id="TF-ALFA2-TEST-02",
        issued_by="toyfoundry_ai_0",
        target="toyfoundry_ai_0",
        priority="standard",
        timestamp_issued="2025-10-29T01:00:00Z",
        summary_override=None,
        narrator=None,
        extra_fields=None,
    )

    assert payload["summary"] == translator.summary
    assert payload["telemetry_stub"]["status"] == translator.telemetry_stub["status"]
