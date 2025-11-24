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

## Next Implementation Steps
- Wire the HUD counters into the thin UI and emit telemetry to `logs/order-2025-11-23-060-m1-playtest.jsonl`.
- Add revive + extraction timers to the HUD overlay; gate all inputs through the emoji DSL.
- Run a stub playtest and capture cadence/emitter logs plus HUD metrics; log to `exchange/ledger/2025-11.md` with evidence paths.
