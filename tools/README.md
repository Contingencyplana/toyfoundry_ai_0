# Toyfoundry Tools

Automation that supports Toyfoundry’s manufacturing pipeline:

- **Manufacturing Order Watcher (`manufacturing_order_watcher.py`)** – Scans the `exchange/` submodule for orders targeting Toyfoundry, highlights outstanding acknowledgements and reports, and can run continuously with `--watch` to notify the factory crew. Forge-related directives include a quick command hint and point to telemetry emitted by the mint ritual.
- **Forge Mint Alfa Ritual (`forge/forge_mint_alfa.py`)** – Generates Alfa manifests from recipes or ad-hoc parameters while emitting telemetry at `.toyfoundry/telemetry/forge_mint_alfa.jsonl`. Supports dry runs for validation or persistent manifest writes for production.
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
