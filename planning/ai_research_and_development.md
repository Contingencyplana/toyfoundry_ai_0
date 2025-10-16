# ?? ai_research_and_development.md - AI R&D Doctrine  
*Frontline Handbook - `high_command_ai_0/planning/`*
---
## ?? Purpose
Establishes how R&D operates across the lattice: how ideas are proposed, prototyped, trialed, measured, and either promoted or retired with safety and provenance.
---
## ?? R&D Cells (War-Tables)
- Location: High Command war-rooms host an **R&D** table (see `planning/war_rooms_and_war_tables.md`).
- Mission: Turn field signals into hypotheses and doctrine updates without breaking cadence or tone.
- Interface: Pair each R&D table with Field Alfas running drills (see `planning/field_workspaces.md`).
---
## ?? Operating Model
1) Intake & Triage: Capture proposals with hypothesis, risks, evaluation metrics, and expected signals.
2) Design Review (RFC): Lightweight RFC with scope, safety notes (Dayland/Nightland), exit criteria.
3) Prototype & Manufacturing: Use Toyfoundry Forge to mint versioned builds with manifests and build info.
4) Trial Execution: Schedule drills; run limited ticks; collect structured telemetry.
5) Telemetry & Loom: Roll up via quilt looms into composite exports for comparative analysis.
6) Deliberation & Decision: R&D tables review efficacy, tone, and risk; decide Promote / Iterate / Quarantine / Archive.
7) Promotion & Doctrine: Emit doctrine update or order; wire into automation; record provenance.
---
## ?? Quickstart
- Draft RFC: create `RFC.md` with scope, risks, exit criteria.
- Mint prototype: `python -m tools.forge.forge_mint_alfa`
- Run trial and collect telemetry.
- Stitch rollups: `python -m tools.telemetry.quilt_loom`
- Export CSV/JSON: `python -m tools.telemetry.quilt_loom --export`
- Review exports: `.toyfoundry/telemetry/quilt/exports/`
---
## ?? Standard Artifacts
- `RFC.md` - intent, scope, risks, exit criteria.
- `experiment.manifest.json` - parameters, inputs, outputs, versioning.
- `risk_notebook.json` - hazards, mitigations, checkpoints.
- `build_info.json` - commit, timestamp, forge recipe, reproducibility hash.
- `run_logs.jsonl` - trial events; Alfa reports.
- Quilt rollups - composite CSV/JSON exports (e.g., `.toyfoundry/telemetry/quilt/exports/composite_export.json` and `.toyfoundry/telemetry/quilt/exports/composite_export.csv`). Generate via `python -m tools.telemetry.quilt_loom --export`.
- `decision_memo.md` - R&D verdict and next actions.
---
## ??? Governance & Safety
- Lattice Alignment: Mirror rank and lattice structure (see `planning/rank_structure.md`, `planning/high_command.md`).
- Tone & Entropy: Monitor Daylands/Nightlands thresholds (see `planning/daylands_and_nightlands.md`).
- Dark Signs: Use `planning/heart_of_darkness.md` checks during trials; pause on flags.
- Containment: Quarantine Nightland Alfas; never delete; repair or archive with notes.
---
## ?? Metrics & Signals (examples)
- `entropy_index`, morale/tonal indicators, terrain balance.
- success/defect rates, stability across ticks, emergence notes.
- build provenance coverage and schema compliance.
---
## ?? Phased Capacity
- Phase 1 - 256 trials (1 Golf): Validate loops, schemas, and tone management.
- Phase 2 - ~1,000 trials (4 Golfs): Comparative experiments; cross-family coordination.
- Phase 3 - 4,096 trials (Juliett): Networked emergence with strong safeguards and automation.
---
## ?? Field Maxim
> R&D advances only as fast as safety, clarity, and provenance allow-measure twice, trial once, promote when rhythm holds.
*End of Scroll - `ai_research_and_development.md`*

