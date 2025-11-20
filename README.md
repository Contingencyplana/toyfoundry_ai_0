# Toyfoundry Workspace

## Overview

Toyfoundry is the manufacturing wing of the SHAGI programme. This workspace hosts the playable-manufacturing experiments that translate High Command orders into factory, telemetry, and narrative outcomes. It is aligned to the Five Major Pivots; for full doctrine see `new_major_pivots/README.md`.

## Current Status — 20 Nov 2025

- Batch 2 (order-2025-11-19-060) baseline frozen at `production/mass_alfa_batch2/`, Alfa-M06…M11 hydrated into their golf targets, and hello reports staged under `outbox/reports/hello-Alfa-M0[6-11]-20251120T01*.json`.
- Offline Continuity Mode is active: the bidirectional `tools/offline_bridge.py` push/pull workflow keeps `C:\Users\Admin\high_command_exchange` in sync, and readiness snapshots (`python tools/ops_readiness.py`) are run before each hydration.
- Order-046 report + acknowledgement synced; telemetry samples (TF-EMOJI-DRYRUN-01/02) remain available for Toysoldiers validation.
- Awaiting downstream acknowledgements for the new batch before catching the trooptrain to the other Genesis fronts.

## Critical Directories

- `planning/` — Strategic briefs, campaign glossaries, hybrid phasing, and Toyfoundry doctrine.
- `.toyfoundry/telemetry/` — Composite exports, canary batches, manifests, and checksums for audit.
- `exchange/` — Order acknowledgements, completion reports, and ledger journal.
- `new_major_pivots/` — Specifications for all pivots plus the Everything At Once meta-paradigm.

## Active Workstreams

| Stream | Lead Docs | Next Milestone |
|--------|-----------|----------------|
| Batch 2 Hydration | `production/mass_alfa_batch2/` | Await downstream pulls + acknowledgements |
| Offline Continuity | `tools/offline_bridge.py`, `tools/exchange_heartbeat.py` | Keep hub sync healthy prior to trooptrain tour |
| Factory Order Integration | `tools/factory_order_emitter.py` | Promote translator payloads under `factory-order@1.0` |
| Telemetry Quilt | `.toyfoundry/telemetry/quilt/exports/` | Maintain validator parity post-orders |

## Getting Oriented

1. Read `planning/toyfoundry/toyfoundry.md` for the factory doctrine and command structure.
2. Review the latest exchange artifacts under `exchange/reports/` and `exchange/acknowledgements/` (Batch 2 hellos + Order-046 completion) and, if needed, mirror them into `exchange/outbox/` before running the bridge.
3. Use the quilt exports to verify current production state before issuing new orders, then run `python tools/ops_readiness.py` to capture a readiness snapshot prior to any new hydration work.

## Reporting

Report updates and new telemetry to High Command via the exchange protocol. Summaries for each corrective action should include regenerated checksums, validator evidence, and storyboard notes that map back to the Five Major Pivots.

---

## Python commands
- Readiness: `python -m tools.ops_readiness`
- Exchange (validate + sync): `python tools/exchange_all.py`
