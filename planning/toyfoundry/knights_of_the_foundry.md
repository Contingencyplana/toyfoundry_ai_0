# Knights of the Foundry

**Status:** Draft doctrine aligned with Toyfoundry canary operations.

## Mission

- Guard Toyfoundry forges whenever new light is minted or exported.
- Execute the canary vigil (or its playable variant) for the full observation window.
- Deliver trustworthy telemetry and narrative reports to High Command and the Valiant Citadel.

## Oath of Vigilance

> We hold the forge in light, we read the freed for truth, and we report without fear or delay.

## Roles During Canary Windows

- **Lead Knight (Vision Holder on duty):** Coordinates the watch, verifies pre-flight checklists, signs the closure note.
- **Wave Knights:** Run the vigil loop, monitor telemetry, call out anomalies, and maintain the Forge Clarity Index.
- **Chronicler:** Captures session notes, timestamps, and attaches evidence (hashes, validator outputs, observations).

## Duties

1. Confirm the forge build, exports, and manifests are stable before the vigil opens.
2. Run the canary checklist or `playable_canary_watch.md` loop for four hours, including overtime if clarity thresholds are missed.
3. Log every wave to `.toyfoundry/telemetry/vigil/` with accurate metrics and annotations.
4. Escalate immediately if the Harmony Meter or Forge Clarity Index drops below safety thresholds.
5. File the after-action note to `high_command_exchange/reports/inbox` and brief the Valiant Citadel reviewer.

## Coordination with the Valiant Citadel

- Toyfoundry owns the playable ritual and frontline telemetry.
- The Valiant Citadel receives the logs, replays high-risk segments if needed, and confirms the closure outcome.
- Closure requires both the Knight commander (Vision Holder) and the assigned Citadel analyst to co-sign the report.

## Relationship to Playable Canary Watch

- The ritual specification is tracked in `planning/toyfoundry/playable_canary_watch.md` (proposal).
- Knights validate that build data, manifests, and validator outputs align with the playable loop before starting a session.
- Any change to the playable design requires Knight testing plus Citadel sign-off prior to doctrine updates.

## Escalation Paths

- **Operational anomalies:** Notify High Command immediately, pause the vigil, quarantine affected exports.
- **Telemetry drift with no immediate cause:** Pull in Citadel analysts for joint investigation before resuming.
- **Personnel fatigue:** Rotate Knights or request Citadel stand-in support; never compromise continuous oversight.

## Standing Orders

- Maintain readiness kits: validator scripts, checksum tools, ritual scripts, reporting templates.
- Keep soft comms open with Citadel controllers throughout the watch window.
- Archive each vigil bundle for historical audits and training scenarios.
