# Playable Canary Watch Proposal

**Status:** Proposal (Pending Implementation)

## Purpose

- Translate the four-hour canary observation window into an embodied Toyfoundry ritual.
- Give Knights of the Foundry a guided loop that mirrors real vigilance: defend, discern, report.
- Produce structured telemetry the Valiant Citadel can audit before certifying the window closed.

## Vigil Rhythm

- **Wave Length:** 10 minutes total.
  - **Storm Phase (7 min):** Defend the forge against hostile glyph streams.
  - **Reading Phase (3 min):** Inspect allied glyphs for corrupted rhythm, hue, or cadence.
- **Session Length:** 24 waves (4 hours) plus optional overtime if clarity thresholds are missed.
- **Lore Hook:** "When new light is forged, the Knights hold vigil: seven minutes holding the line, three minutes reading the freed."

## Core Mechanics

- **Controls:** Three lanes (left, center, right); single light-pulse action to cleanse hostile glyphs.
- **Harmony Meter:** Tracks accuracy and timing; falling below 70% restarts the current wave.
- **Discernment Lens:** Activates during Reading Phase; hover or tap to flag false allies.
- **Respawn Rule:** Failed waves replay at the same difficulty; cleared waves increase pace and density.

## Scoring and Outcomes

- **Forge Clarity Index (FCI):** Composite score from enemies cleansed, anomalies found, false flags avoided, and completion tempo.
- **Outcomes:**
  - FCI  0.90: Forge clean, window closed.
  - 0.70  FCI < 0.90: Extended vigil, repeat two waves.
  - FCI < 0.70: Escalate to High Command for manual review.

## Telemetry and Reporting

- Log each wave to `.toyfoundry/telemetry/vigil/forge_<timestamp>.jsonl` with hits, misses, anomalies_found, fci, duration_ms.
- Append session summary to `high_command_exchange/reports/inbox`.
- Vision Holder issues the formal closure note once both Toyfoundry telemetry and Valiant Citadel review align.

## Ownership and Review Path

- **Primary Steward:** Toyfoundry Knights of the Foundry (operational duty, ritual execution, telemetry capture).
- **Safety Review:** Valiant Citadel consumes the telemetry, checks anomalies, and co-signs the closure report.
- **Change Control:** Promote this proposal into doctrine only after prototype playtests and Citadel approval.

## Implementation Notes

- Keep combat stylised: light, rhythm, choral cues instead of violence.
- Provide a one-minute boot sequence for calibration and briefing.
- Include a five-minute reflection template for Knights to file after-action notes.
- Document the mapping from in-game metrics to operational trust signals to aid Citadel audits.
