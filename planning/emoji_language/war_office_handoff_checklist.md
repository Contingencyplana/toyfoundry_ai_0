# War Office Narration Handoff Checklist

**Purpose:** Ensure Toyfoundry can deliver narration-ready assets once the translator module graduates from spike status. This checklist keeps payload summaries, narration lines, and War Office coordination in lockstep with the `quint_synced` specifications.

---

## 1. Alignment Inputs

- `quint_synced/payload_alignment.md` — Canonical schema contract for `factory-order@1.0`.
- `quint_synced/narration_alignment.md` — Lore delivery guidance and pronunciation notes.
- Translator spike outputs (`translator_round_trips.jsonl`, Level-0 samples) for validation references.

## 2. Pre-Handoff Tasks

1. **Schema Confirmation**
   - [ ] Validate translator payloads via `tools/factory_order_emitter.py --dry-run` to ensure schema compliance.
   - [ ] Confirm `summary` strings mirror narration line verbatim.
   - [ ] Verify `telemetry_stub` metrics align with Order 021 expectations (batch_id, ritual, duration).

2. **Narration Prep**
   - [ ] Collect narrator persona requirements from War Office (default: herald).
   - [ ] Note localisation priorities and required fallback language list.
   - [ ] Assemble beat timing (`beats` array) for each glyph chain so VO pacing matches gameplay.

3. **Asset Packaging**
   - [ ] Produce `payload_summary.csv` (order_id, summary, glyph_chain) for rapid review.
   - [ ] Generate `narration_script.md` with one section per glyph chain, including pronunciation cues.
   - [ ] Export round-trip evidence from translator spike for War Office QA.

## 3. Delivery Window

- Preferred submission channel: Exchange attachments under `exchange/orders/outbox/emoji_runtime/`.
- Notify War Office via High Command once assets uploaded; include checksum manifest.
- Archive signed-off scripts in `planning/emoji_language/archives/` (create if needed).

## 4. Post-Handoff Follow-Up

- [ ] Log successful handoff in `quint_synced/README.md` sync table (include War Office initials).
- [ ] Update `tools/factory_order_emitter.py` metadata defaults with War Office narrator code-name if supplied.
- [ ] Capture feedback items and open follow-up tasks in High Command order tracker.

---

**Status:** Drafted 2025-10-26 pending War Office review.

Use this checklist during the payload+narration sync so every workspace hands over identical, lore-aligned assets without additional reconciliation passes.
