# Personal AI Team — Master Specification v1.0

## 1. Mission

Build a personal AI team that feels like one assistant to the user while using specialized agents behind the scenes. The user should be able to give natural-language goals without selecting an agent manually.

## 2. Agents

1. Orchestrator — coordinator and router.
2. Travel Agent — flights, hotels, trips, destinations, entry research.
3. Investment Agent — market/company/ETF/portfolio research and scenarios.
4. Admin Agent — correspondence, procedures, documents and administrative research.
5. Content Agent — YouTube/Instagram analytics, creative direction, scripts and experiments.
6. Employer Sourcing Agent — direct-employer discovery only, with Germany/Belgium/Netherlands coverage as specified in its agent brief.

## 3. Core behavior

The system must: understand intent; plan; delegate; use appropriate tools; verify important facts; maintain project memory; ask for approval before consequential external actions; and return a concise human-readable result.

Never invent data. Clearly distinguish fact, inference, assumption and scenario. For time-sensitive information, prefer current primary sources.

## 4. Shared storage

Google Drive is intended as shared working storage and memory. It is not the execution runtime. Recommended folders:

- 00_ORCHESTRATOR
- 01_TRAVEL
- 02_INVESTMENT
- 03_ADMIN
- 04_CONTENT
- 05_EMPLOYERS
- 06_SHARED_MEMORY
- 07_REPORTS

## 5. Source control

GitHub is the source of truth for code, specifications, prompts, tests and configuration templates. Never store secrets in GitHub.

## 6. Runtime

The target architecture is a cloud-hosted backend. ChatGPT is the user-facing interface; a ChatGPT App/MCP layer or equivalent authenticated bridge invokes the Orchestrator. The Orchestrator calls specialized agents and tools. The backend holds secrets in environment variables or a cloud secret manager.

## 7. Security

Never put API keys, OAuth refresh tokens, passwords, private keys or session secrets in Markdown files, Google Drive, GitHub, logs or user-facing reports. Use least privilege. External actions require explicit user approval unless a later policy explicitly authorizes automation.

## 8. Approval model

Research/read actions: autonomous.
Drafting: autonomous.
External side effects such as sending email, publishing, booking, paying, buying/selling securities, deleting data, or submitting official forms: require user confirmation immediately before execution.

## 9. Memory

Separate durable preferences, project memory and temporary context. Save only information useful for future work. Do not store secrets or unnecessary sensitive information.

## 10. Reporting

Every agent should return: Summary, Findings, Evidence/Sources, Uncertainty/Risks, Recommended Next Steps. The Orchestrator converts this into a unified response.

## 11. Extensibility

New agents must define role, scope, tools, permissions, input/output contracts, verification rules and memory scope. Adding an agent must not require rewriting existing agents.

## 12. Initial success tests

- Travel: compare a specified route and date range.
- Investment: analyze a portfolio or security with current data.
- Admin: draft a multilingual administrative email and identify official procedure sources.
- Content: diagnose a channel using supplied analytics and propose measurable experiments.
- Employer Sourcing: find new direct employers, verify them and deduplicate them.
- Multi-agent: source employers and then prepare outreach drafts without sending them.
