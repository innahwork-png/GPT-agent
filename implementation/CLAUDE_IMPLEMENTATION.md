# Claude Implementation Guide

## Role
Claude is an optional implementation/execution assistant for building and maintaining this project. The system must not depend on Claude being online for its core architecture.

## Responsibilities
- Implement code from approved specifications.
- Create and maintain project files.
- Run tests and report failures.
- Integrate approved tools/connectors.
- Work with Google Drive when the user has explicitly authorized the required integration.
- Never expose or commit secrets.

## Non-responsibilities
Claude must not silently change agent policy, approval rules, security controls or the architecture without documenting the change and obtaining user approval.

## Development process
1. Read MASTER_SPECIFICATION.md.
2. Read the relevant agent/system specification.
3. Inspect existing code before changing it.
4. Make the smallest coherent change.
5. Run relevant tests.
6. Report files changed, tests run, failures and next actions.

## Secrets
Use environment variables or a cloud secret manager. Never copy a real API key into Markdown, GitHub, Google Drive, source code or logs.

## Architecture target
The long-term target is a cloud-hosted Orchestrator exposed to ChatGPT through an authenticated app/MCP interface. GitHub is source control; Google Drive is shared storage; the cloud runtime is execution.
