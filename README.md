# Toyfoundry Workspace

## Overview

Toyfoundry is the manufacturing wing of the SHAGI programme. This workspace hosts the playable-manufacturing experiments that translate High Command orders into factory, telemetry, and narrative outcomes. It is aligned to the Five Major Pivots; for full doctrine see `new_major_pivots/README.md`.

## Current Status — 26 Oct 2025

- Order-036 remediation completed; regenerated exports validated and reported to High Command.
- Pivot Five (emoji-first language bridge) alignment acknowledged; `tools/factory_order_emitter.py` ready for translator integration.
- Narration handoff checklist drafted (`planning/emoji_language/war_office_handoff_checklist.md`) pending War Office asset delivery.
- Exchange acknowledgements and reports are current; awaiting High Command integration orders after cross-workspace sync.

## Critical Directories

- `planning/` — Strategic briefs, campaign glossaries, hybrid phasing, and Toyfoundry doctrine.
- `.toyfoundry/telemetry/` — Composite exports, canary batches, manifests, and checksums for audit.
- `exchange/` — Order acknowledgements, completion reports, and ledger journal.
- `new_major_pivots/` — Specifications for all pivots plus the Everything At Once meta-paradigm.

## Active Workstreams

| Stream | Lead Docs | Next Milestone |
|--------|-----------|----------------|
| Alfa Zero | `docs/alfa_zero_spec.md` | Phase 1 static grid renderer |
| Pivot Five | `new_major_pivots/new_major_pivot_5.md` | Finalize Level-0 glyph grammar |
| Factory Order Integration | `tools/factory_order_emitter.py` | Promote translator payloads under `factory-order@1.0` |
| Telemetry Quilt | `.toyfoundry/telemetry/quilt/exports/` | Maintain validator parity post-orders |

## Getting Oriented

1. Read `planning/toyfoundry/toyfoundry.md` for the factory doctrine and command structure.
2. Review the latest exchange artifacts under `exchange/reports/` and `exchange/acknowledgements/`.
3. Use the quilt exports to verify current production state before issuing new orders.

## Reporting

Report updates and new telemetry to High Command via the exchange protocol. Summaries for each corrective action should include regenerated checksums, validator evidence, and storyboard notes that map back to the Five Major Pivots.

---

## Python commands
- Readiness: `python -m tools.ops_readiness`
- Exchange (validate + sync): `python tools/exchange_all.py`
