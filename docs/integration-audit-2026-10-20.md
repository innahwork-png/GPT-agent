# Integration audit — 2026-10-20

## Verified
- GitHub connector authenticated as innahwork-png.
- Repository innahwork-png/GPT-agent readable and writable through connector.
- README describes Phase 1 architecture and states Phase 2 cloud runtime/ChatGPT integration is future work.
- requirements.txt contains FastAPI, OpenAI Agents SDK, Supabase, pytest and httpx.
- .env.example contains placeholders only.

## Not verified
- A deployed, executing Orchestrator or scheduled worker.
- Routing to all four projects at runtime.
- Railway backend health, environment variables and deployment linkage.
- Supabase project connection, tables, policies and credentials.
- End-to-end workflow tests and monitoring.

## Changes in this audit
- AGENTS.md central operating policy.
- agents/orchestrator.md routing and validation contract.
- agents/general-assistant.md fourth-project specification.

## Acceptance criteria for operational status
1. Running backend exposes authenticated health and routing diagnostics.
2. Each project passes at least one harmless smoke test.
3. Supabase and Railway are verified using their live connectors.
4. Logs and failures are observable, and authorization gates work.
5. User confirms any necessary production deployment or sensitive configuration.

Documentation alone does not satisfy these acceptance criteria.
