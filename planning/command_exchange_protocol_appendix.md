# Appendix — CI & Hooks (HC Alfa Pilot)

- Pre-commit hooksPath: point git to `exchange/.githooks/`.
  - Example: `git config core.hooksPath exchange/.githooks`
- Validator command used in hook: `python tools/schema_validator.py <json_paths>`
- Guardrails config: `tools/hc_alfa_pilot.config.json` defines allowlisted paths, rate limits, and lockfile.
- All HC Alfa scripts run with `--dry-run` by default; human approval required before apply.

## Scheduling Daily Briefings (example)

- Runner: `tools/hc_alfa/run_briefing.ps1`
- Windows Task Scheduler example:
  - `schtasks /Create /SC DAILY /TN "HC_Alfa_Briefing" /TR "pwsh -File tools\hc_alfa\run_briefing.ps1" /ST 09:00`
- Cron (Linux/macOS) example:
  - `0 9 * * * pwsh -File tools/hc_alfa/run_briefing.ps1`

## Ledger Indexer

- Rebuild `exchange/ledger/index.json` from filesystem state:
  - Dry-run: `python tools/ledger_indexer.py --dry-run`
  - Write: `python tools/ledger_indexer.py --write`
