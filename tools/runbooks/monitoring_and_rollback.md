# Monitoring and Rollback Runbooks

Monitors
- Ingestion/validation exit codes
- Report acceptance status (blocked != green)
- Checksum mismatches
- Error rate / latency in canary

On Alert
- Freeze: stop further rollout; communicate status
- Diagnose: logs, diffs, metrics
- Decide: rollback vs. fix-forward

Rollback Steps
- Identify last good snapshot/build
- Restore artifacts and repoint paths
- Record rollback_reason in build_info
- Emit report with remediation notes

Postmortem
- Capture timeline, root cause, action items
- Update safety gates/checklists

