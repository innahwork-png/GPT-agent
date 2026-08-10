from dataclasses import dataclass

from .agents import AGENTS
from .sdk_agents import SPECIALIZED_AGENTS


@dataclass(frozen=True)
class Route:
    agent: str
    reason: str
    requires_multi_agent: bool = False


class Orchestrator:
    """Route user tasks to the appropriate specialized agent."""

    def route(self, task: str) -> Route:
        text = task.lower()
        rules = (
            (("flight", "hotel", "travel", "trip", "visa", "перелет", "отель", "поездк"), "travel"),
            (("stock", "etf", "portfolio", "invest", "valuation", "акци", "инвест", "портфел"), "investment"),
            (("letter", "email", "register", "close", "document", "письм", "зарегистр", "закрыт"), "admin"),
            (("youtube", "instagram", "content", "script", "channel", "ютуб", "инстаграм", "канал", "сценар"), "content"),
            (("employer", "job", "construction", "solar", "harvest", "warehouse", "factory", "работ", "работодател", "строитель", "солнеч", "склад", "завод"), "employer_sourcing"),
        )
        for keywords, agent_name in rules:
            if any(keyword in text for keyword in keywords):
                return Route(
                    agent=agent_name,
                    reason=f"Matched task keywords for {agent_name}.",
                    requires_multi_agent=self._looks_multi_agent(text),
                )
        return Route(agent="orchestrator", reason="No specialized route matched; orchestration decision required.")

    def available_agents(self):
        return [agent.name for agent in AGENTS]

    def get_sdk_agent(self, name: str):
        return SPECIALIZED_AGENTS[name]

    @staticmethod
    def _looks_multi_agent(text: str) -> bool:
        markers = ("and", "also", "потом", "и затем", "подготовь письмо", "сравни", "затем")
        return sum(marker in text for marker in markers) >= 1
