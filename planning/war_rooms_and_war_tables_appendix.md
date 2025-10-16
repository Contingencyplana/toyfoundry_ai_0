# Appendix — Approvals Workflow (HC Alfa Pilot)

- Flow: dry-run -> human approval -> apply.
- Dry-run: All HC Alfa scripts operate with `--dry-run` and write intent to `logs/hc_alfa/*.jsonl`.
- Approval: A human Safety Officer signs off on the proposed mutation (orders moved, ledger updates) before apply.
- Apply: Mutation proceeds within allowlisted paths; pre-commit validator must pass; actions are rate-limited and lockfile-protected.

