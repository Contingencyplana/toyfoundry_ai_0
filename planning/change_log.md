# Change Log

All notable updates to the High Command AI workspace are documented here. Entries reference corresponding orders and ledger notes.

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
