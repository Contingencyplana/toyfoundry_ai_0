# Toyfoundry Tools

Automation that supports Toyfoundry’s manufacturing pipeline:

- **Manufacturing Order Watcher (`manufacturing_order_watcher.py`)** – Scans the `exchange/` submodule for orders targeting Toyfoundry, highlights outstanding acknowledgements and reports, and can run continuously with `--watch` to notify the factory crew. Forge-related directives include a quick command hint and point to telemetry emitted by the mint ritual.
- **Exchange Watcher (`exchange_watcher.py`)** – Lightweight polling utility that lists pending orders, acknowledgements, and reports for any target and keeps a change snapshot in `.toyfoundry/telemetry/exchange_watcher_state.json`.
- **Schema Validator (`schema_validator.py`)** – CLI check that ensures orders, acknowledgements, and reports include required keys. Designed for pre-commit or ad-hoc validation of JSON payloads.
- **Forge Mint Alfa Ritual (`forge/forge_mint_alfa.py`)** – Generates Alfa manifests from recipes or ad-hoc parameters while emitting telemetry at `.toyfoundry/telemetry/forge_mint_alfa.jsonl`. Supports dry runs for validation or persistent manifest writes for production.
- **Forge Ritual Stubs (`forge/forge_drill_alfa.py`, `forge/forge_parade_alfa.py`, `forge/forge_purge_alfa.py`, `forge/forge_promote_alfa.py`)** – Skeleton commands for the remaining Toyfoundry rituals that log telemetry to `.toyfoundry/telemetry/forge_rituals.jsonl` via `forge/ritual_logger.py`.
- **Telemetry Quilt Loom (`telemetry/quilt_loom.py`)** – Aggregates mint telemetry into `.toyfoundry/telemetry/quilt/quilt_rollup.json` so High Command can inspect batch trends at a glance.
- **Forge Adapters** – _Planned._ Adapter scripts will translate manufacturing recipes into Forge-compatible manifests, attach safety rail validators, and emit batch telemetry in the factory format.
- **Batch Telemetry Quilt** – _Planned._ Tooling to stitch together production metrics (entropy, emergence, release readiness) into dashboards for Parades and governance reviews.

Run the watcher once:

```powershell
python -m tools.manufacturing_order_watcher --exchange exchange --target toyfoundry_ai_0
```

Or watch continuously:

```powershell
python -m tools.manufacturing_order_watcher --watch --interval 60
```

Mint a dry-run Alfa prototype:

```powershell
python -m tools.forge.forge_mint_alfa --name prototype-001 --dry-run --param color=cerulean
```

Stitch the telemetry quilt:

```powershell
python -m tools.telemetry.quilt_loom
```

Run the exchange watcher once:

```powershell
python -m tools.exchange_watcher --exchange exchange --target toyfoundry_ai_0
```

Validate an order payload:

```powershell
python -m tools.schema_validator exchange/orders/pending/order-2025-10-12-007.json
```
