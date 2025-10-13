# production_plan.md — Toyfoundry Manufacturing Kickoff

## 1. Purpose

Establish the initial production posture for Toyfoundry following Order 2025-10-12-005. This plan defines target batch sizes, diversity ratios, telemetry capture, and automation hooks that align with the Q4 2025 Operational Charter.

## 2. Batch Cadence

| Phase | Batch Size | Notes |
|:--|:--|:--|
| Pilot Run (Week 1) | 12 Alfas | Dry-run batches using `forge_mint_alfa --dry-run` to validate telemetry and ritual stubs. |
| Expansion (Week 2) | 48 Alfas | Introduce mutation parameters and partial execution of Drill and Parade rituals. |
| Operational Baseline (Week 3+) | 96 Alfas per sprint | Continuous manufacturing with quotas for mutation, baseline refresh, and experimental recipes. |

## 3. Diversity Targets

- **Novel Parameters:** ≥ 60% of each batch must introduce at least one new parameter permutation.
- **Mutation Carryover:** 20% of each batch allocated to successful mutations promoted from prior runs.
- **Baseline Refresh:** 20% of each batch recreates canonical patterns to maintain stability and regression coverage.
- **Safety Budget:** Every run passes through validator hooks; failures are logged and retried only after human review.

## 4. Telemetry Quilt Inputs

| Signal | Source | Description |
|:--|:--|:--|
| Mint Ledger | `.toyfoundry/telemetry/forge_mint_alfa.jsonl` | Individual mint attempts (dry-run flag, seed, recipe). |
| Ritual Log | `.toyfoundry/telemetry/forge_rituals.jsonl` | Drill, Parade, Purge, Promote invocations with batch metadata. |
| Watcher Snapshot | `.toyfoundry/telemetry/exchange_watcher_state.json` | Last-seen exchange artefacts for traceability. |
| Composite Quilt | `.toyfoundry/telemetry/quilt/quilt_rollup_all.json` | Consolidated view of mint plus ritual telemetry for each Alfa operation. |
| Manufacturing Reports | `exchange/reports/*` | Aggregated outcomes per order or batch. |

The telemetry quilt loom (`python -m tools.telemetry.quilt_loom`) ingests these feeds, stitches per-batch summaries (status, outcome, defects), and exports daily dashboards for High Command.

## 5. Automation Hooks

- **Exchange Watcher:** `python -m tools.exchange_watcher --target toyfoundry_ai_0 --watch` scheduled every 5 minutes.
- **Manufacturing Order Watcher:** `python -m tools.manufacturing_order_watcher --watch --interval 30` for Toyfoundry-specific cues.
- **Schema Validator:** Pre-commit hook invoking `python -m tools.schema_validator` on modified exchange artefacts.
- **Ritual Scripts:** Forge stubs (`forge_*.py`) emit telemetry for every invocation, enabling the loom to produce stitched summaries.

## 6. Risks & Mitigations

- **Telemetry Drift:** Mitigated through schema validator enforcement and nightly lint of telemetry feeds.
- **Automation Gaps:** Watcher scripts run on schedule and emit audible notifications when pending orders change.
- **Capacity Overrun:** Batch sizes scale gradually (12 → 96) with human checkpoints before each expansion.

## 7. Next Steps

1. Run mint and composite telemetry quilt loom rollups nightly and feed reports into Order 2025-10-12-008 follow-ups.
2. Extend Forge adapters to hydrate manifests with recipe packs and push results to toysoldiers.
3. Formalise promotion criteria and connect to doctrine archives for long-term storage.
