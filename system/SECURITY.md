# Security

## Secrets
Never commit real API keys, OAuth tokens, passwords, cookies, private keys or session secrets. Use environment variables locally and a managed secret store in production.

## Least privilege
Every integration should receive only the scopes it needs. Read-only tools should not receive write access.

## External actions
Require explicit user confirmation immediately before consequential actions: sending messages, publishing, booking, payments, trades, purchases/sales, deletion, official submissions and account changes.

## Logging
Do not log secrets or full authentication material. Logs should contain safe identifiers and operational status only.

## Data handling
Store only the minimum data needed for the task. Avoid unnecessary sensitive data. Respect connector-specific permissions and user revocation.

## Repository
`.env`, credential files and secret-bearing local configuration must be ignored by version control. Only `.env.example` belongs in the repository.
