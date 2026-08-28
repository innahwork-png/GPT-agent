from dataclasses import dataclass

from .agents import AGENTS
from .models import AgentResult
from .runtime import run_agent
from .sdk_agents import SPECIALIZED_AGENTS


@dataclass(frozen=True)
class Route:
    agent: str
    reason: str
    requires_multi_agent: bool = False


class Orchestrator:
    """Route tasks and execute specialized or general agents through the SDK."""

    def route(self, task: str) -> Route:
        text = task.lower()
        rules = (
            (("flight", "hotel", "hotels", "travel", "trip", "visa", "отел", "гостиниц", "перелет", "перелёт", "авиабилет", "поездк", "путешеств", "курорт", "рейс"), "travel"),
            (("stock", "etf", "portfolio", "invest", "valuation", "акци", "инвест", "портфел", "оценк компании"), "investment"),
            (("letter", "email", "register", "close", "document", "письм", "зарегистр", "закрыт", "документ", "справк"), "admin"),
            (("youtube", "instagram", "content", "script", "channel", "ютуб", "инстаграм", "контент", "канал", "сценар"), "content"),
            (("employer", "job", "construction", "solar", "harvest", "warehouse", "factory", "работ", "работодател", "строитель", "солнеч", "склад", "завод", "ваканс"), "employer_sourcing"),
        )
        for keywords, agent_name in rules:
            if any(keyword in text for keyword in keywords):
                return Route(
                    agent=agent_name,
                    reason=f"Matched task keywords for {agent_name}.",
                    requires_multi_agent=self._looks_multi_agent(text),
                )
        # General requests should go to the general agent instead of failing.
        return Route(agent="general", reason="No specialist keyword matched; using the general AI agent.")

    async def run_task(self, task: str) -> AgentResult:
        route = self.route(task)
        if route.agent not in SPECIALIZED_AGENTS:
            raise ValueError(f"Agent is not configured: {route.agent}")
        return await run_agent(route.agent, task)

    def available_agents(self):
        return [agent.name for agent in AGENTS] + ["General"]

    def get_sdk_agent(self, name: str):
        return SPECIALIZED_AGENTS[name]

    @staticmethod
    def _looks_multi_agent(text: str) -> bool:
        markers = ("and", "also", "потом", "также", "и затем", "подготовь письмо", "сравни", "затем")
        return sum(marker in text for marker in markers) >= 1
