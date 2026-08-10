from dataclasses import dataclass

from .agents import AGENTS


@dataclass(frozen=True)
class Route:
    agent: str
    reason: str


class Orchestrator:
    """Thin coordination layer; agent execution will be wired to the Agents SDK next."""

    def route(self, task: str) -> Route:
        text = task.lower()
        rules = (
            (("flight", "hotel", "travel", "trip", "visa"), "travel"),
            (("stock", "etf", "portfolio", "invest", "valuation"), "investment"),
            (("letter", "email", "register", "close", "document"), "admin"),
            (("youtube", "instagram", "content", "script", "channel"), "content"),
            (("employer", "job", "construction", "solar", "harvest", "warehouse", "factory"), "employer_sourcing"),
        )
        for keywords, agent_name in rules:
            if any(keyword in text for keyword in keywords):
                return Route(agent=agent_name, reason=f"Matched task keywords for {agent_name}.")
        return Route(agent="orchestrator", reason="No specialized route matched; orchestration decision required.")

    def available_agents(self):
        return [agent.name for agent in AGENTS]
