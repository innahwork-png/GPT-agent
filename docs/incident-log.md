# Incident and lessons log

Use this file as the durable audit history. Do not include secrets, personal data or raw tokens.

| Date | Project | Issue | Root cause / evidence | State | Next verification |
|---|---|---|---|---|---|
| 2026-10-20 | Orchestrator | Documentation described Phase 1 while a Railway runtime was already deployed | README stale; Railway service GPT-agent linked to main, healthy after deploy | mitigated | Update README to actual runtime status |
| 2026-10-20 | Routing | Existing specialized agents and four user-facing ChatGPT projects were not explicitly mapped | Added projects.py, API endpoints and tests; no confirmed authenticated end-to-end response yet | open | Run CI and authenticated smoke tests |
| 2026-10-20 | Monitoring | No persistent monthly incident review process | Added quality-evolution policy and monthly review schedule | mitigated | Confirm first report and record incidents |
| 2026-10-20 | Observability | agent_runs/tasks tables had zero records at time of audit | Supabase schema exists; execution instrumentation not verified | open | Verify whether run_task writes audit rows |
