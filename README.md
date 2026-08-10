# Personal AI Team

A modular personal AI agent system with a central Orchestrator and specialized agents for Travel, Investment, Administration, Content, and Direct Employer Sourcing.

## Architecture

- **Orchestrator** — routes tasks, plans multi-agent workflows, verifies results, and coordinates permissions.
- **Travel Agent** — flights, hotels, trips, destinations, entry research.
- **Investment Agent** — market, company, ETF, portfolio, and scenario research.
- **Admin Agent** — administrative procedures, correspondence, and document assistance.
- **Content Agent** — YouTube/Instagram analytics, creative direction, scripts, and experiments.
- **Employer Sourcing Agent** — direct-employer discovery in Germany, Belgium, and the Netherlands across construction, harvest/agriculture, solar/PV, factories, warehouses, sorting, and packaging.

## Security

Never commit API keys, passwords, tokens, or other secrets. Use environment variables or a cloud secret manager. `.env.example` contains placeholders only.

## Project status

Phase 1: architecture and specifications.

Phase 2: cloud runtime and ChatGPT integration will be added after the specification layer is finalized.
