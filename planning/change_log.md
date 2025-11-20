# Change Log

All notable updates to the High Command AI workspace are documented here. Entries reference corresponding orders and ledger notes.

## 2025-11-20

- **Daily Doc Refresh — README.md** — Captured Batch 2 (order-2025-11-19-060) hydration completion, Offline Continuity Mode posture, and exchange telemetry notes so High Command has a current readiness snapshot before the next trooptrain sync.

## 2025-10-12

- **Order 2025-10-12-001** — Issued first exchange directive; toysoldiers_ai_0 stood up receiver, produced ack/report, and order closed in ledger.
- **Order 2025-10-12-002** — Directed toysoldiers_ai_0 to align acknowledgement/report payloads with official schemas and implement expiry warnings.
- **Order 2025-10-12-003** — Mandated governance collateral (MIT license, Code of Conduct, Contributing guide) across toysoldiers_ai_0; exchange ledger updated after acknowledgement/report cycle.
- **Exchange Watcher v1** — Introduced `tools/exchange_watcher.py` with tests to surface new orders/acks/reports automatically; recommended for deployment in all theatres, including Toyfoundry’s manufacturing floor.
- **Doctrine Glossary** — Added `planning/glossary.md` capturing shared acronyms, terminology, and tooling references for High Command, Toyfoundry manufacturing, and field theatres.
- **Toyfoundry Charter Q4 2025** — Expanded `planning/toyfoundry/toyfoundry.md` with mission scope, interfaces, guardrails, and upcoming orders to prepare the manufacturing pipeline rollout.
- **Toyfoundry Governance Collateral** — Added root `LICENSE`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md` aligned with Toyfoundry’s manufacturing mission.
- **Manufacturing Order Watcher** — Implemented `tools/manufacturing_order_watcher.py` to monitor the exchange submodule for Toyfoundry-targeted orders and outstanding acknowledgements.
- **Forge Mint Ritual** — Added `tools/forge/forge_mint_alfa.py`, updated watcher integration, and recorded telemetry plumbing for Alfa mint dry-runs.

## 2025-10-13

- **Order 2025-10-12-005** — Delivered Forge ritual stubs (`forge_drill_alfa.py`, `forge_parade_alfa.py`, `forge_purge_alfa.py`, `forge_promote_alfa.py`) with shared telemetry logging and published `planning/toyfoundry/production_plan.md`.
- **Exchange Automation** — Added `tools/exchange_watcher.py` and `tools/schema_validator.py` to keep Toyfoundry in sync with High Command orders and enforce JSON payload integrity.
- **Telemetry Quilt Loom** — Stood up `.toyfoundry/telemetry/quilt/` scaffolding and `tools/telemetry/quilt_loom.py` to aggregate Alfa mint telemetry into a rollup for Order 2025-10-12-007.
- **Order 2025-10-12-008** — Expanded the telemetry quilt loom to ingest Drill/Parade/Purge/Promote streams, emit composite rollups, and documented the new schema fragments.
- **Order 2025-10-12-009** - Added export schema documentation, automated JSON/CSV exports via the quilt loom, and published sample artefacts under `.toyfoundry/telemetry/quilt/exports/`.

## 2025-10-16

- **AI R&D Doctrine** — Added `planning/ai_research_and_development.md` with R&D operating model, Quickstart, and export paths aligned to quilt loom outputs.
- **AI Labscapes & Labs Guide** — Added/updated `planning/ai_labscapes_and_ai_labs.md` with lifecycle, Quickstart, and normalized separators (Alfa -> Juliett; Hypothesis -> Archive).

## 2025-10-18

- **Four Major Pivots Adoption** — Toyfoundry embraced the Four Major Pivots framework from `new_major_pivots/`: (1) 70% play / 30% dev-ops ratio, (2) playable workflow overlay with 16×16 emoji battlegrids replacing VSCode/PowerShell, (3) SHAGI vision maintenance through aesthetic grid design, (4) fractal folder structure `golf_00/` through `golf_15/` supporting 4,096 Alfas.
- **Seven Pivotal Fronts Integration** — Aligned Toyfoundry operations with High Command's Seven Pivotal Fronts structure (Toyfoundry = Front 5 Manufacturing). Added `planning/pivotal_fronts_pointer.md` linking to canonical `planning/pivotal_fronts/README.md` and documenting cross-front coordination with Safety, R&D, Field Ops, and Operations.
- **Playable Manufacturing Vision** — Updated `planning/toyfoundry/toyfoundry.md` with strategic alignment section (§9) explaining how Forge rituals transform into tactical missions, emoji grid visualization, and gameplay-driven order execution.
- **Initial Alfa Prototype Planning** — Scoped `golf_00/delta_00/alfa_00/` as first playable workflow demonstration: 16×16 emoji grid wired to Forge ritual execution, telemetry feedback as grid state updates, victory condition = satisfied High Command order via grid clicks.
