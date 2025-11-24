# Campaign 1 UI/HUD Integration Plan (for Toyfoundry)

Purpose: provide a concrete integration target so Toyfoundry can wire the thin UI/HUD, route inputs through the emoji DSL/guardrails, and run a live playtest to close Campaign 1 (ORDER-060).

## Targets and Dates
- Locked dates (HC): M1=2025-11-28, M3=2025-12-05.
- Toyfoundry targets (per ACK): M1 core loop 2025-11-27; thin UI/telemetry 2025-11-30; M3 playtest slice 2025-12-03.

## Expected UI Surface
- Minimal battlegrid/observer HUD with:
  - Role select + confirmation.
  - Ability quick-cast mapped to emoji DSL (textless inputs).
  - Ping/target selection via emoji DSL.
  - HUD indicators: health/stamina, revive prompt, extraction timer, “one more run?” prompt.
- All UI input events must pass through the emoji DSL/guardrails; no raw unguarded inputs.

## Input Contract (emit these events to the runtime)
Emit JSON events to the game/runtime and persist alongside telemetry (`logs/order-2025-11-23-060-m1-ui-live.jsonl` format is acceptable). Required fields:
```json
{
  "ts": "2025-11-24T12:00:00Z",
  "event": "emoji_input",
  "actor": "operator_id",
  "action": "role_select|ability_cast|ping",
  "emoji": "⚔️",
  "target": "enemy|ally|objective|none"
}
```
Guardrails: if an input is blocked, log `event: "guardrail_block"` with the same fields plus `"reason"`.

## Telemetry Contract (append to JSONL and export)
Write to `logs/order-2025-11-23-060-m1-ui-live-telemetry.json` (and mirror to hub). Required fields per event:
- `trace_id`: stable per run (e.g., `c1-ui-<timestamp>`).
- `run_id`: match cadence run id if available.
- `event`: one of `ttf_start`, `ttf_end`, `revive`, `one_more_prompt`, `emoji_latency_sample`, `ui_state`.
- `metrics`: object with event-specific data, e.g.:
  - `ttf_start/ttf_end`: `{ "t_ms": <int> }` (Time-to-Fun delta).
  - `revive`: `{ "count": <int> }`.
  - `one_more_prompt`: `{ "accepted": true|false }`.
  - `emoji_latency_sample`: `{ "ms": <int>, "action": "<emoji>" }`.
  - `ui_state`: `{ "hud_visible": true|false, "battlegrid_active": true|false }`.

## Runtime Hooks (expected)
- On UI input: send emoji DSL event to runtime; if blocked, log guardrail event and show user-safe feedback.
- On HUD updates: emit `ui_state` telemetry with HUD visibility and battlegrid status.
- On prompts: log `one_more_prompt` with accepted/declined.
- On revive: log `revive` increments.

## Evidence to Produce
- Live playtest logs from the actual UI run:
  - `logs/order-2025-11-23-060-m1-ui-live.jsonl` (input stream with guardrail blocks).
  - `logs/order-2025-11-23-060-m1-ui-live-telemetry.json` (metrics as above).
- Cadence + emitter smoke for the run: `tools/end_of_block.py` and `tools/factory_order_emitter.py --help` logs.
- Ledger entry with evidence paths and run timestamp.
- Completion report for Campaign 1 referencing the above.

## Steps for Toyfoundry (apply in their workspace)
1) Wire UI inputs to emit the JSON event contract above, enforcing emoji DSL/guardrails.
2) Add HUD telemetry hooks to emit `ui_state`, `revive`, `one_more_prompt`, and `emoji_latency_sample`.
3) Run a live playtest on the actual UI (not the CLI sim) to generate the two log files listed above.
4) Run cadence + emitter smoke, stash logs under `logs/`, and mirror to the hub (`exchange/outbox/attachments/campaign1/`).
5) Add a ledger entry with evidence paths; file the Campaign 1 completion report.

## Acceptance
Campaign 1 closes when a real UI/HUD playtest is logged with the required telemetry and cadence/emitter evidence, and the completion report is filed. Sim tools alone are not sufficient.
