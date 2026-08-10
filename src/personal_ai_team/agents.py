from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str


AGENTS = (
    AgentSpec("travel", "Flights, hotels, trips, destinations, and entry research."),
    AgentSpec("investment", "Investment and market research, valuation, portfolio analysis, and scenarios."),
    AgentSpec("admin", "Administrative procedures, correspondence, and document assistance."),
    AgentSpec("content", "YouTube/Instagram analytics, creative direction, scripts, and experiments."),
    AgentSpec("employer_sourcing", "Direct-employer sourcing in Germany, Belgium, and the Netherlands."),
)


def get_agent(name: str) -> AgentSpec:
    normalized = name.strip().lower().replace("-", "_")
    for agent in AGENTS:
        if agent.name == normalized:
            return agent
    raise KeyError(f"Unknown agent: {name}")
