# Toyfoundry Tools

Automation that supports Toyfoundry’s manufacturing pipeline:

- **Manufacturing Order Watcher (`manufacturing_order_watcher.py`)** – Scans the `exchange/` submodule for orders targeting Toyfoundry, highlights outstanding acknowledgements and reports, and can run continuously with `--watch` to notify the factory crew.
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
