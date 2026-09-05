from dataclasses import dataclass

from .agents import AGENTS
from .models import AgentResult
from .runtime import run_orchestrator
from .sdk_agents import SPECIALIZED_AGENTS


@dataclass(frozen=True)
class Route:
    agent: str
    reason: str
    requires_multi_agent: bool = False


class Orchestrator:
    """Central manager: route for observability, then delegate execution to the SDK manager."""

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
        return Route(agent="general", reason="No specialist keyword matched; using the general AI agent.")

    async def run_task(self, task: str) -> AgentResult:
        """Run the central SDK manager so it can choose and combine specialist agents."""
        return await run_orchestrator(task)

    def available_agents(self):
        return [agent.name for agent in AGENTS] + ["General"]

    @staticmethod
    def _looks_multi_agent(text: str) -> bool:
        markers = ("and", "also", "потом", "также", "и затем", "подготовь письмо", "сравни", "затем")
        return sum(marker in text for marker in markers) >= 1
