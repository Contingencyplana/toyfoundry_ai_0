# Toyfoundry Alfa Two — Implementation Task Plan

**Updated:** 2025-10-29

This plan captures the concrete engineering steps to execute once GitHub access is restored. All items map back to the mission brief and High Command’s standing assignments.

## 1. Translator / Factory Bridge

1. Promote Toysoldiers payload samples into the repo under `tests/alfa_two/`.
2. Implement a lightweight wrapper script that calls `tools/factory_order_emitter.py` for each glyph ritual triggered by Alfa Two.
3. Extend `tools/factory_order_emitter.py` metadata block with the War Office narrator persona once provided.
4. Wire emitted payloads into `exchange/orders/outbox/emoji_runtime/` with run IDs (`TF-ALFA2-<timestamp>`).

*Status (2025-10-29): Fixtures staged and `tools/alfa_two_emit.py --dry-run` ready to fan out rituals; live emission awaits War Office go.*

## 2. Validator Integration

1. Create `tests/alfa_two/test_factory_payloads.py` with unit tests covering happy path and schema mismatch scenarios using the new emitter.
2. Add a CI hook (once GitHub returns) invoking `python tools/validate_order_021.py` against staged exports before merge.
3. Document validator expectations in `planning/alfa_two_validation.md` (new file) and link from the mission brief.

*Status (2025-10-29): `tests/alfa_two/test_factory_payloads.py` plus validation guide capture success/failure paths; CI hook to follow once GitHub unlocks.*

## 3. Monitoring Hooks

1. Fork `tools/manufacturing_order_watcher.py` into `tools/alfa_two_monitor.py` to watch emitted payloads, flag narration/summary drift, and capture glyph mismatches.
2. Emit monitoring results to `monitoring/logs/narrator_metrics.json` and `monitoring/logs/glyph_vo_discrepancies.log`.
3. Preserve baselines under `monitoring/baselines/TF-ALFA2-*.json` for regression comparisons.
4. Coordinate with Valiant Citadel to surface metrics on their dashboards (post-sync task).

## 4. Morningate + Reporting

1. Build export templates in `exports/factory_orders/` and `exports/feeds/battle_reports/` with placeholders for run IDs and summaries.
2. Update `planning/morningate_reflection_layer.md` Section 8 once the first Alfa Two run produces actionable insights.
3. Prepare a `reports/alfa_two_postrun.md` template capturing anomalies, telemetry, and recommendations for Toysoldiers.

## 5. Coordination & Sync

1. Log War Office checkpoints (pre-launch approval, payload audit, narration alignment, post-run debrief) in `planning/emoji_language/war_office_handoff_checklist.md` as they are cleared.
2. Mirror `quint_synced/` updates back to High Command and peer workspaces after each modification.
3. Keep Order-036 and Order-2025-10-20-001 under observation; be ready to execute once unlock notices arrive.

*Next update scheduled after GitHub access is restored or new directives land.*
