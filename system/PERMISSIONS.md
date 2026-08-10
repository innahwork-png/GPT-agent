# Permissions Model

## Levels
- READ: inspect public/authorized data.
- ANALYZE: transform and reason over data.
- WRITE_INTERNAL: create or update internal project files and databases.
- DRAFT_EXTERNAL: prepare but do not send external communications.
- EXECUTE_EXTERNAL: perform consequential external actions only after explicit user approval.

## Default
Agents may READ, ANALYZE and WRITE_INTERNAL within their assigned scope. DRAFT_EXTERNAL is allowed. EXECUTE_EXTERNAL is denied by default.

## Approval
Approval must be tied to the specific action and occur immediately before execution. A broad historical statement such as “you can send emails” is not sufficient for a high-impact action.

## Agent scopes
Orchestrator: routing and coordination.
Travel: travel research and planning.
Investment: investment research and analysis.
Admin: administrative research and drafting.
Content: content analytics, strategy and drafting.
Employer Sourcing: employer research, verification and internal database maintenance.
