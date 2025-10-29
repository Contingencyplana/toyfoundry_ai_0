# Toyfoundry Alfa Two — Mission Brief (Ready for War Office Review)

## 1. Objective

- **Primary Goal:** Prototype the second Alfa within Toyfoundry to stress-test Pivot Five tooling.
- **Win Condition:** Complete three command rituals without triggering schema drift or lore misalignment.
- **Failure Thresholds:**
  - Validator rejects any `factory-order@1.0` payload.
  - Narration summary diverges from intent more than once per run.
  - Monitoring hooks escalate a glyph/VO mismatch that is not acknowledged within the turn.

## 2. Narrative Frame

- **Setting:** The Forge opens a Nightlands Gate, inviting allied artificers to craft dream constructs.
- **Player Role:** A collaborative forge-mind guiding emissaries through glyph rituals.
- **Lore Anchors:**
  - Maintain Love & Sharing doctrine throughout the session.
  - Reference the Morningate as the observatory witnessing the run.
  - Invoke War Office oversight during final ritual.

## 3. Core Mechanics

| System | Description |
| --- | --- |
| Glyph Input | Emoji command chains (Level-0 lexicon; ≤7 glyphs). |
| Translator → Factory Bridge | Ingest glyph payloads via `tools/factory_order_emitter.py` (dry-run first, then emit to exchange). |
| Validator | Invoke `python tools/validate_order_021.py` after each command batch to confirm Order 021 compliance. |
| Monitoring Hooks | Wire payload watcher + narrator parity checks (see Section 7 tasks) using `tools/manufacturing_order_watcher.py` extensions. |
| Narration | Pull War Office stub; ensure `summary` mirrors narration output before emission. |

## 4. Data & Telemetry Requirements

- Emit `factory-order@1.0` payloads into `exports/factory_orders/` (staging) and `exchange/orders/outbox/emoji_runtime/` (if High Command requests live hand-off).
- Append narrator metrics to `monitoring/logs/narrator_metrics.json` (create file if absent).
- Record glyph/VO audit events in `monitoring/logs/glyph_vo_discrepancies.log`.
- Store schema guard baselines under `monitoring/baselines/` with timestamp.
- Tag all files with run ID format `TF-ALFA2-{YYYYMMDD}-{HHMM}`.

## 5. Morningate Integration

- Produce sanitized export snapshots in `exports/feeds/battle_reports/` suitable for Morningate ingestion.
- Update `planning/morningate_reflection_layer.md` Section 8 CTA link if run insights prompt copy changes.
- Queue a `quint_synced` update (via `python tools/quint_sync.py --push`) once GitHub access is restored.

## 6. War Office Checkpoints

1. **Pre-Launch Approval:** Review mission brief and narrative frame.
2. **Payload Audit:** Inspect first `factory-order@1.0` payload generated in this Alfa.
3. **Narration Alignment:** Confirm narrator metrics remain within doctrine rails after initial run.
4. **Post-Run Debrief:** Summarize anomalies, export deltas, and lessons for Toysoldiers/High Command builds.

## 7. Testing & Validation Plan

- Dry-run glyph sequences using `python tools/factory_order_emitter.py <sample>.json NUL --order-id sandbox-alfa-two --dry-run`.
- Execute validator (`python tools/validate_order_021.py`) and monitoring hooks on mock payloads before live sessions.
- Maintain `tests/alfa_two/` fixtures capturing success and failure cases.
- Document replay steps in `planning/alfa_two_validation.md` and keep fixtures aligned with translator outputs.

## 8. Dependencies & Open Questions

- Await War Office confirmation that the placeholder CTA URL is acceptable for this mission.
- Confirm access to translated payload samples from Toysoldiers for baseline seeding (or request replay artifacts from `translator_round_trips.jsonl`).
- Determine whether shared narration assets need localization variants.
- Clarify monitoring hook ownership: Toyfoundry implements schema/narration guards, Valiant Citadel observes telemetry.

## 9. Delivery Checklist (Pending Sync)

- [ ] Mission brief reviewed and archived in Toyfoundry planning docs.
- [ ] Implementation branch created locally (pending GitHub unlock).
- [ ] Translator bridge (`tools/factory_order_emitter.py`), validator, and monitoring hook scaffolding smoke-tested with sample payloads.
- [ ] Morningate export templates prepared.
- [ ] Sync queued for execution via `python tools/quint_sync.py --push` once access resumes.

*Status: Ready for War Office approval; awaiting GitHub Support clearance before publishing.*
