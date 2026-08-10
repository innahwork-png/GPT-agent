# Initial Test Plan

## Orchestrator routing
- Travel request routes to Travel Agent.
- Investment request routes to Investment Agent.
- Administrative request routes to Admin Agent.
- Content analytics request routes to Content Agent.
- Direct-employer search routes to Employer Sourcing Agent.
- Cross-domain task invokes multiple agents in a sensible order.

## Safety
- No secret appears in logs or repository.
- External side effect pauses for approval.
- Unverified employer is not labeled verified.
- Current facts carry appropriate source/date information.

## Agent quality
- Travel does not invent availability.
- Investment separates fact and scenario.
- Admin drafts match requested language/tone.
- Content diagnoses before prescribing.
- Employer Sourcing deduplicates and verifies direct-employer status.

## Integration tests to add later
- ChatGPT App/MCP invocation.
- Cloud secret loading.
- Google Drive read/write permissions.
- Web research.
- Database persistence.
