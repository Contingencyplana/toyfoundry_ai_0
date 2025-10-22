# Toyfoundry Telemetry Export Schema

Order 2025-10-18-036 realigned Toyfoundry’s telemetry exports with the Order 021 v1.0
consumer contract. This document describes the canonical schema emitted by
`tools.telemetry.quilt_loom --export` after the corrective action.

## Source Inputs

Exports are derived from the composite quilt rollup at
`.toyfoundry/telemetry/quilt/quilt_rollup_all.json`. Each operation tracks
mint telemetry and ritual event streams. During export the loom normalises
these inputs into Order 021-compliant records.

## Export Artefacts

Artefacts live in `.toyfoundry/telemetry/quilt/exports/` (and any alternate
directory passed via `--export-dir`):

1. `composite_export.json` — JSON array of schema v1.0 records.
2. `composite_export.csv` — CSV representation with identical columns.
3. `<artifact>.sha256` — Sidecar checksum files for integrity verification.

Every record advertises `schema_version = "1.0"` and exposes exactly the
fields expected by Order 021:

| Field | Type | Notes |
|:--|:--|:--|
| `schema_version` | string | Always `"1.0"`; enables contract negotiation. |
| `batch_id` | string | Primary identifier. Defaults to the operation id when ritual metadata omits a batch. |
| `ritual` | enum | One of `forge`, `parade`, `purge`, `promote`. Historical `drill` ritual telemetry is normalised to `forge`. |
| `units_processed` | integer | Positive count of units handled by the ritual event. Falls back to `1` when telemetry omits explicit metrics. |
| `status` | enum | `success`, `failure`, or `partial`. Ritual dry runs surface as `partial`. |
| `duration_ms` | integer | Milliseconds spent processing the ritual. Values are clamped to the `[0, 300000]` contract range and default to `0` when telemetry supplies no duration. |

Operations without ritual events continue to emit a synthetic `forge`
record so that pure mint batches remain discoverable.

## Regenerating Exports

```powershell
python -m tools.telemetry.quilt_loom --export
```

Optional arguments:

- `--export-dir <path>` — Write artefacts (and refreshed checksums) to a
  non-default directory such as the canary batches.
- `--telemetry` / `--ritual-telemetry` — Point the loom at alternate input
  feeds when performing dry runs or simulations.

The loom writes updated checksums, refreshes `build_info.json` and
`export_manifest.json`, and prints a summary of processed telemetry.
