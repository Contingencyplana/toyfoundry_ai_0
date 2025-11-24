# Campaign 1 - Core Loop (Toyfoundry)

This slice captures the M1 Nightlands co-op loop with quick role select, 1–2 enemy archetypes, and thin HUD instrumentation. Inputs must stay under the emoji DSL/guardrails.

## Roles (emoji DSL)
- Sentinel (`🛡️`): signature ability `🛡️✨` (shield pulse) routes through emoji DSL; baseline attack `⚔️`.
- Caster (`✨`): signature ability `✨🌑` (void tether) routes through emoji DSL; baseline attack `⚔️`.

## Enemy Archetypes
- Wraith (`👻`): dashes to backline; weak to `🛡️✨`.
- Husk (`💀`): slow melee; weak to `✨🌑`.

## Thin HUD / Telemetry Hooks
- Time-to-Fun (TTF): time from role lock to first ability cast; log under `hud.time_to_fun_ms`.
- Revive cadence: track down -> revive delta per player; log under `hud.revive_ms`.
- “One more run?” prompt: present after extraction; log acceptance under `hud.one_more_accept`.

## Evidence Stub
- `production/campaign1/m1_core_loop_prototype.json` (emoji-runtime@1.0) captures the loop intent and HUD hooks; promotable via `python tools/emoji_runtime_promoter.py production/campaign1/m1_core_loop_prototype.json exchange/orders/outbox/emoji_runtime_promoted/order-2025-11-23-060-m1.json`.
- `tools/campaign1_playtest_stub.py` emits a stub playtest log with HUD metrics and emoji events.
- `tools/campaign1_hud_telemetry.py` computes HUD metrics + guardrail checks from a playtest log.
- `tools/campaign1_hud_sim.py` generates a thin-UI playtest log with configurable timings (TTF, revive, extraction, one-more-run).
- `tools/campaign1_ui_runner.py` is the thin-UI runner that emits emoji-only events and HUD metrics for live runs; feed its output into `campaign1_hud_telemetry.py` for reports.

## Next Implementation Steps
- Wire the HUD counters into the thin UI and emit telemetry to `logs/order-2025-11-23-060-m1-playtest.jsonl`.
- Add revive + extraction timers to the HUD overlay; gate all inputs through the emoji DSL.
- Run a stub playtest and capture cadence/emitter logs plus HUD metrics; log to `exchange/ledger/2025-11.md` with evidence paths.
