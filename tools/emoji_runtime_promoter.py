"""Promote emoji-runtime@1.0 payloads into factory-order@1.0 documents."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

try:
    from tools.factory_order_emitter import (
        PayloadValidationError,
        TranslatorPayload,
        build_factory_order,
        write_factory_order,
    )
except ModuleNotFoundError:  # pragma: no cover - script execution fallback
    import sys

    REPO_ROOT = Path(__file__).resolve().parents[1]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from tools.factory_order_emitter import (
        PayloadValidationError,
        TranslatorPayload,
        build_factory_order,
        write_factory_order,
    )

EMOJI_RUNTIME_SCHEMA = "emoji-runtime@1.0"
DEFAULT_OUTPUT_DIR = Path("exchange/orders/outbox/emoji_runtime_promoted")


class EmojiRuntimeValidationError(PayloadValidationError):
    """Raised when an emoji-runtime payload cannot be promoted."""


@dataclass
class EmojiRuntimePayload:
    summary: str
    glyph_chain: Sequence[str]
    intent: Mapping[str, Any]
    telemetry_stub: Mapping[str, Any]
    narration_line: str | None
    narration_beats: Sequence[str] | None
    timestamp: str | None
    directives: Sequence[Any]
    outcomes: Sequence[Any] | None
    template: str | None
    raw: Mapping[str, Any]

    @property
    def checksum(self) -> str:
        canonical = json.dumps(self.raw, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _ensure_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EmojiRuntimeValidationError(f"emoji-runtime field '{field}' must be an object")
    return value


def _ensure_sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise EmojiRuntimeValidationError(f"emoji-runtime field '{field}' must be an array")
    return value


def _validate_glyph_chain(payload: Mapping[str, Any]) -> Sequence[str]:
    raw_chain = payload.get("glyph_chain") or payload.get("raw") or payload.get("emoji_chain")
    if raw_chain is None:
        raise EmojiRuntimeValidationError("emoji-runtime payload missing glyph chain (glyph_chain/raw)")
    chain = _ensure_sequence(raw_chain, "glyph_chain")
    cleaned: list[str] = []
    for index, glyph in enumerate(chain):
        if not isinstance(glyph, str) or not glyph.strip():
            raise EmojiRuntimeValidationError(f"glyph_chain[{index}] must be a non-empty string glyph")
        cleaned.append(glyph)
    if not cleaned:
        raise EmojiRuntimeValidationError("glyph_chain cannot be empty")
    return cleaned


def _validate_telemetry_stub(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    telemetry = payload.get("telemetry_stub")
    telemetry_map = _ensure_mapping(telemetry, "telemetry_stub")
    required = {
        "batch_id": str,
        "ritual": str,
        "units_processed": int,
        "status": str,
        "duration_ms": int,
    }
    for field, expected in required.items():
        if field not in telemetry_map:
            raise EmojiRuntimeValidationError(f"telemetry_stub missing '{field}'")
        value = telemetry_map[field]
        if not isinstance(value, expected):
            raise EmojiRuntimeValidationError(
                f"telemetry_stub field '{field}' must be {expected.__name__}, found {type(value).__name__}"
            )
        if expected is int and value < 0:
            raise EmojiRuntimeValidationError(f"telemetry_stub field '{field}' must be non-negative")
    return telemetry_map


def _extract_narration(payload: Mapping[str, Any]) -> tuple[str | None, Sequence[str] | None]:
    narration = payload.get("narration")
    if narration is None:
        spoken = payload.get("spoken")
        if isinstance(spoken, Sequence) and not isinstance(spoken, (str, bytes)):
            return None, [str(item) for item in spoken]
        return None, None

    if isinstance(narration, str):
        return narration, None

    narration_map = _ensure_mapping(narration, "narration")
    line = narration_map.get("line") or narration_map.get("summary")
    beats = narration_map.get("beats") or narration_map.get("spoken")
    beats_seq = None
    if beats is not None:
        beats_seq = _ensure_sequence(beats, "narration.beats")
    return (line if isinstance(line, str) else None, beats_seq)


def load_emoji_runtime_payload(path: Path) -> EmojiRuntimePayload:
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    if raw_data.get("schema") != EMOJI_RUNTIME_SCHEMA:
        raise EmojiRuntimeValidationError(
            f"emoji-runtime payload schema must be '{EMOJI_RUNTIME_SCHEMA}', found '{raw_data.get('schema')}'"
        )

    summary = raw_data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise EmojiRuntimeValidationError("emoji-runtime payload must include non-empty 'summary'")

    glyph_chain = _validate_glyph_chain(raw_data)
    intent = _ensure_mapping(raw_data.get("intent"), "intent")
    telemetry = _validate_telemetry_stub(raw_data)
    narration_line, narration_beats = _extract_narration(raw_data)

    timestamp = None
    for key in ("timestamp", "timestamp_generated", "generated_at", "created_at"):
        value = raw_data.get(key)
        if isinstance(value, str) and value:
            timestamp = value
            break

    directives = raw_data.get("directives")
    if directives is None and isinstance(raw_data.get("template"), str):
        directives = [raw_data["template"]]
    directives_seq = []
    if directives is not None:
        directives_seq = list(_ensure_sequence(directives, "directives"))

    outcomes = None
    if raw_data.get("outcomes") is not None:
        outcomes = list(_ensure_sequence(raw_data["outcomes"], "outcomes"))

    template = raw_data.get("template") if isinstance(raw_data.get("template"), str) else None

    return EmojiRuntimePayload(
        summary=summary.strip(),
        glyph_chain=glyph_chain,
        intent=intent,
        telemetry_stub=telemetry,
        narration_line=narration_line.strip() if narration_line else None,
        narration_beats=[str(beat) for beat in narration_beats] if narration_beats else None,
        timestamp=timestamp,
        directives=directives_seq,
        outcomes=outcomes,
        template=template,
        raw=raw_data,
    )


def build_factory_order_from_emoji(
    payload: EmojiRuntimePayload,
    *,
    order_id: str,
    issued_by: str,
    target: str,
    priority: str,
    timestamp_issued: str,
    summary_override: str | None = None,
    narrator: str | None = None,
    extra_fields: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    translator = TranslatorPayload(
        summary=payload.summary,
        glyph_chain=list(payload.glyph_chain),
        intent=dict(payload.intent),
        telemetry_stub=dict(payload.telemetry_stub),
        narration_line=payload.narration_line,
        narration_beats=list(payload.narration_beats) if payload.narration_beats else None,
        raw=payload.raw,
    )
    factory_order = build_factory_order(
        translator,
        order_id=order_id,
        issued_by=issued_by,
        target=target,
        priority=priority,
        timestamp_issued=timestamp_issued,
        summary_override=summary_override,
        narrator=narrator,
        extra_fields=extra_fields,
    )

    metadata = factory_order.setdefault("metadata", {})
    metadata.setdefault("emoji_runtime_schema", EMOJI_RUNTIME_SCHEMA)
    if payload.timestamp:
        metadata.setdefault("emoji_runtime_timestamp", payload.timestamp)
    metadata.setdefault("emoji_runtime_checksum_sha256", payload.checksum)
    if payload.template:
        metadata.setdefault("emoji_runtime_template", payload.template)
    if payload.outcomes:
        metadata.setdefault("emoji_runtime_outcomes", list(payload.outcomes))

    if payload.directives:
        factory_order.setdefault("directives", list(payload.directives))

    return factory_order


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote emoji-runtime@1.0 payloads into factory-order@1.0 documents",
    )
    parser.add_argument("emoji_payload", type=Path, help="Path to emoji-runtime@1.0 payload JSON")
    parser.add_argument(
        "destination",
        type=Path,
        nargs="?",
        help="Destination for the emitted factory-order JSON (defaults to output directory)",
    )
    parser.add_argument("--order-id", required=True, help="Factory order identifier")
    parser.add_argument("--issued-by", default="toyfoundry_ai_0", help="ID of the issuing workspace")
    parser.add_argument("--target", default="toyfoundry_ai_0", help="Factory order target workspace")
    parser.add_argument("--priority", default="standard", help="Factory order priority flag")
    parser.add_argument(
        "--timestamp",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        help="Timestamp for the factory order (defaults to current UTC time)",
    )
    parser.add_argument(
        "--summary",
        help="Optional override for the lore-facing summary (must align with narration if provided)",
    )
    parser.add_argument("--narrator", help="Optional War Office narrator persona to embed in metadata")
    parser.add_argument(
        "--extra-field",
        action="append",
        metavar="KEY=VALUE",
        help="Additional top-level fields to merge (value must be JSON)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the emitted payload without writing to disk",
    )
    return parser.parse_args(argv)


def _parse_extra_fields(pairs: Sequence[str] | None) -> Dict[str, Any]:
    extras: Dict[str, Any] = {}
    if not pairs:
        return extras
    for pair in pairs:
        if "=" not in pair:
            raise EmojiRuntimeValidationError(
                f"Invalid extra-field specification '{pair}'. Expected KEY=JSON_VALUE"
            )
        key, raw_value = pair.split("=", 1)
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise EmojiRuntimeValidationError(f"extra-field '{key}' must be valid JSON: {exc}") from exc
        extras[key] = value
    return extras


def main(argv: Iterable[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = load_emoji_runtime_payload(args.emoji_payload)
        extras = _parse_extra_fields(args.extra_field)

        destination = args.destination
        if destination is None:
            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            destination = DEFAULT_OUTPUT_DIR / f"{args.order_id}.json"

        factory_order = build_factory_order_from_emoji(
            payload,
            order_id=args.order_id,
            issued_by=args.issued_by,
            target=args.target,
            priority=args.priority,
            timestamp_issued=args.timestamp,
            summary_override=args.summary,
            narrator=args.narrator,
            extra_fields=extras,
        )

        if args.dry_run:
            print(json.dumps(factory_order, indent=2))
            print("(dry run) factory-order validated; no file written")
        else:
            write_factory_order(factory_order, destination)
            print(f"factory-order emitted to {destination}")
        return 0
    except EmojiRuntimeValidationError as exc:
        print(f"Promotion aborted: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
