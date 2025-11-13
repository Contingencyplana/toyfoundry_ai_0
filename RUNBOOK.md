# toyfoundry_ai_0 — Runbook (v1)

Purpose: turn High Command Alfa directives into validated factory output (orders, telemetry, lore) without breaking the Forge→Drill→Parade→Purge→Promote cadence.

Core Objectives
- Keep `python -m tools.ops_readiness` green before pulling or publishing exchange artifacts.
- Follow the Foundry Cycle for every Alfa batch: blueprint → recipe → simulation → parade report → archive.
- Maintain traceability by updating `exchange/ledger/index.json`, telemetry quilts, and storyboard notes for each order ID.
- Report upstream via `python tools/exchange_all.py` only when orders, acknowledgements, and reports are paired and validated.

Operator Loop (per shift)
1. Warm start: run readiness; fix missing docs or staged files immediately.
2. Intake: `python tools/exchange_all.py` (pull) to mirror hub orders before authoring new work.
3. Forge/Drill: draft or update payloads in `outbox/orders/`, pair `outbox/acks/`, and synthesize `outbox/reports/` using `tools/factory_order_emitter.py` + local sims.
4. Parade/Archive: push validated evidence into `exchange/acknowledgements/`, `exchange/reports/`, and update quilts under `.toyfoundry/telemetry/`.
5. Final gate: rerun readiness, then `python tools/exchange_all.py` (push) to record the run in `logs/exchange_all.json`; ping High Command if new Alfa packages are ready.

Safety + Quality Gates
- Documentation: keep this RUNBOOK, `README.md`, and `planning/toyfoundry/*.md` aligned before shipping.
- Schema: every outbound artifact must pass `tools/factory_order_emitter.py --validate` plus JSON schema checks tied to the current pivot.
- Telemetry: `.toyfoundry/telemetry/quilt/exports/` must include the latest batch with checksums noted in the ledger entry.
- Ledger hygiene: no payload leaves without an `exchange/ledger/index.json` entry citing order ID, pivot, evidence, and sign-off.

Evidence & Logging
- Ops gate: `logs/ops_readiness.json`
- Exchange pushes/pulls: `logs/exchange_all.json`
- Ledger + attachments: `exchange/ledger/`, `exchange/attachments/`
- Telemetry quilt + sims: `.toyfoundry/telemetry/`

Escalation & Contacts
- Halt production if readiness fails twice; resume only after documenting the fix in `planning/change_log.md`.
- Notify High Command when Alfa lots graduate from Parade → Promote so Toysoldiers can schedule integration drills.

References
- `README.md`
- `planning/toyfoundry/toyfoundry.md`
- `new_major_pivots/README.md`
- `tools/factory_order_emitter.py`
