# Toyfoundry Alfa Two — Validation Reference

**Last Updated:** 2025-10-29

## Validator Entry Points

- Run `python tools/validate_order_021.py` after each Alfa Two ritual batch. The command inspects staged exports under `exchange/orders/` and confirms the Order 021 contract.
- Execute `python -m pytest tests/alfa_two/test_factory_payloads.py` to exercise the factory-order emission path on curated fixtures.
- Use `python tools/alfa_two_emit.py --dry-run` to sanity check translator payloads before writing files to the exchange.

## Fixture Library (`tests/alfa_two/`)

| File | Purpose |
| --- | --- |
| `sample_translator_payload.json` | Baseline payload previously validated against Order 021. |
| `sample_translator_payload_scout.json` | Secondary success case covering scouting narration and telemetry. |
| `sample_translator_payload_missing_units.json` | Failure fixture missing `telemetry_stub.units_processed`; ensures guards trip as expected. |

## Expected Outcomes

1. Valid fixtures promote without modification and keep narration line aligned with the lore summary.
2. Any divergence between the `summary` override and narration line raises `PayloadValidationError`.
3. Missing telemetry fields are rejected before emission, preventing malformed exchanges.

## Monitoring Tie-In

- When `tools/alfa_two_emit.py` writes payloads (non `--dry-run`), ensure monitoring hooks ingest the newly written files from `exchange/orders/outbox/emoji_runtime/`.
- Append resulting checksums and narration metrics to the logs defined in the mission brief (`monitoring/logs/narrator_metrics.json`, `monitoring/logs/glyph_vo_discrepancies.log`).

## Follow-Up Actions

- Integrate the pytest target into CI once GitHub access returns.
- Keep this document updated as new fixtures or validator behaviors are introduced.
