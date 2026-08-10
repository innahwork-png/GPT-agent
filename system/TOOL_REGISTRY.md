# Tool Registry

This document defines the intended categories of tools. Concrete providers are implementation choices and must be configured separately.

## Web research
Used for current web pages, official sources, public job boards, travel research and market research.

## Google Drive
Shared document storage and working memory. Not an execution runtime. Must use OAuth/connector authorization; never store credentials in Drive.

## OpenAI API
Used by the cloud runtime for model inference when the deployed architecture requires API calls. The API key belongs in the cloud secret manager/environment, never in GitHub or Drive.

## GitHub
Source control for code, specifications, tests and configuration templates.

## Future tools
Email, calendars, booking providers, market data providers, YouTube/Instagram analytics, databases and other services may be added with least-privilege permissions and explicit action gates.

## Tool selection rule
The Orchestrator should select the smallest set of tools necessary for the task and prefer primary sources for consequential facts.
