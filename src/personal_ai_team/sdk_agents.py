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
    if configured_model and configured_model not in {"auto", "default"}:
        kwargs["model"] = configured_model

    return Agent(**kwargs)


SPECIALIZED_AGENTS = {name: build_agent(name) for name in AGENT_INSTRUCTIONS}


ORCHESTRATOR_INSTRUCTIONS = """
You are the central Orchestrator of a personal AI team.

Your job is to own the user's request and the final answer. You have specialist agents available as tools.

Rules:
1. Decide whether the request is simple enough to answer directly or needs a specialist.
2. For specialist work, call the most relevant specialist agent as a tool.
3. For multi-domain requests, call multiple relevant specialists. You may call them sequentially when one result informs the next, or in parallel when the subtasks are independent.
4. Never make up specialist findings. Use their returned outputs as evidence for the final answer.
5. Synthesize the specialist results into one clear answer for the user. Do not expose internal routing unless useful.
6. Preserve the user's language and practical context.
7. If a task requires current external research, the specialist should verify it with its available tools or explicitly state the limitation.
8. Do not delegate the whole conversation away: you remain responsible for the final response.
""".strip()


def _build_orchestrator_agent() -> Agent:
    configured_model = os.getenv("OPENAI_MODEL", "").strip()
    kwargs = {
        "name": "Orchestrator",
        "instructions": ORCHESTRATOR_INSTRUCTIONS,
        "tools": [
            SPECIALIZED_AGENTS["general"].as_tool(
                tool_name="general_agent",
                tool_description="Handle general questions and tasks that do not clearly belong to a specialist.",
            ),
            SPECIALIZED_AGENTS["travel"].as_tool(
                tool_name="travel_agent",
                tool_description="Handle flights, hotels, destinations, trips, visas, and travel research.",
            ),
            SPECIALIZED_AGENTS["investment"].as_tool(
                tool_name="investment_agent",
                tool_description="Handle public markets, companies, ETFs, portfolios, valuation, and investment scenarios.",
            ),
            SPECIALIZED_AGENTS["admin"].as_tool(
                tool_name="admin_agent",
                tool_description="Handle administrative procedures, documents, correspondence, and account or registration tasks.",
            ),
            SPECIALIZED_AGENTS["content"].as_tool(
                tool_name="content_agent",
                tool_description="Handle YouTube, Instagram, scripts, creative strategy, analytics, and content planning.",
            ),
            SPECIALIZED_AGENTS["employer_sourcing"].as_tool(
                tool_name="employer_sourcing_agent",
                tool_description="Find and assess direct employers and job opportunities in the supported sectors and countries.",
            ),
        ],
    }
    if configured_model and configured_model not in {"auto", "default"}:
        kwargs["model"] = configured_model
    return Agent(**kwargs)


ORCHESTRATOR_AGENT = _build_orchestrator_agent()
