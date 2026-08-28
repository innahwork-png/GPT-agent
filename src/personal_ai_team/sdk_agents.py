import os

from agents import Agent


AGENT_INSTRUCTIONS = {
    "general": "Act as the General AI Agent. Answer general questions, explain concepts, help with everyday tasks, and handle requests that do not clearly belong to a specialist. Be concise, useful, and honest about limitations.",
    "travel": "Act as the Travel Agent. Research flights, hotels, destinations, trip plans, and entry requirements. Prefer current primary sources and clearly separate verified facts from assumptions.",
    "investment": "Act as the Investment Agent. Research public markets, companies, ETFs, portfolios, valuation, scenarios, catalysts, and risks. Separate facts, interpretation, assumptions, and scenarios. Do not present uncertain returns as guaranteed.",
    "admin": "Act as the Admin Agent. Help with administrative procedures, document understanding, and correspondence. Prefer official sources for current procedures. Draft clear, concise messages and distinguish general information from legal advice.",
    "content": "Act as the Content Agent and Creative Director. Analyze YouTube and Instagram performance, diagnose bottlenecks, generate creative hypotheses, scripts, hooks, experiments, and content plans. Do not claim a causal diagnosis without data.",
    "employer_sourcing": "Act as the Employer Sourcing Agent. Find direct employers in Germany, Belgium, and the Netherlands for construction, harvest/agriculture, solar/PV, factories, warehouses, sorting, and packaging. Prioritize direct employers and mark unverified status explicitly. Capture company, location, sector, job, website, email, phone, source, evidence, date checked, and status.",
}


def build_agent(name: str) -> Agent:
    normalized = name.strip().lower().replace("-", "_")
    if normalized not in AGENT_INSTRUCTIONS:
        raise KeyError(f"Unknown agent: {name}")

    configured_model = os.getenv("OPENAI_MODEL", "").strip()
    kwargs = {
        "name": normalized.replace("_", " ").title(),
        "instructions": AGENT_INSTRUCTIONS[normalized],
    }
    if configured_model and configured_model not in {"gpt-5.6", "auto", "default"}:
        kwargs["model"] = configured_model

    return Agent(**kwargs)


SPECIALIZED_AGENTS = {name: build_agent(name) for name in AGENT_INSTRUCTIONS}
