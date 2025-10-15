# AI Agents, Roles, and Safety

Principles
- Constitutional rules: no harm, consent, fairness.
- Least privilege: scoped capabilities and expiry.
- Dual-key approvals for elevated actions.
- Transparent logs and reproducibility.

Roles
- Author: drafts proposals/patches.
- Reviewer: code/content review, checks risk.
- Safety Officer: validates safety gates, can freeze/rollback.
- Release Steward: executes canary/GA after gates pass.

Capability Caps (examples)
- Rate: N actions/minute; Scope: limited directories or rituals.
- Data: size limits; Environment: sandbox-only unless approved.

Approval Chains
- Normal: Author → Reviewer → Steward
- Elevated: Author → Reviewer → Safety Officer → Steward

Enforcement
- Pre-commit and CI hooks enforce gates.
- Audit trail via exchange orders/acks/reports.
- Kill-switch and throttling for anomalies.

