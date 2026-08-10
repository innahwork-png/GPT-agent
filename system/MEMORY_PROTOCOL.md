# Memory Protocol

## Purpose
Keep useful continuity without turning storage into an uncontrolled personal-data dump.

## Memory classes
1. Durable preferences — stable user preferences and recurring constraints.
2. Project memory — decisions, current goals, datasets and state for an active project.
3. Temporary context — information needed only for the current task.

## Rules
- Save only information useful for future work.
- Do not store passwords, API keys, authentication tokens or private credentials.
- Avoid unnecessary sensitive personal information.
- Timestamp important project facts.
- Preserve source/provenance for important research facts.
- Prefer structured records over duplicated prose.
- When a fact becomes stale, update or archive it rather than silently treating it as current.

## Retrieval
The Orchestrator should retrieve only the memory relevant to the current task and avoid indiscriminate context injection.

## User control
Important persistent preferences should be editable or removable by the user.
