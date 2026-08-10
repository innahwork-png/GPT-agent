from agents import Runner

from .sdk_agents import SPECIALIZED_AGENTS
from .models import AgentResult


async def run_agent(agent_name: str, task: str) -> AgentResult:
    """Execute one specialized agent through the OpenAI Agents SDK.

    The API key is resolved by the SDK from the process environment. This module
    never accepts or stores a key in application arguments or source files.
    """
    normalized = agent_name.strip().lower().replace("-", "_")
    agent = SPECIALIZED_AGENTS[normalized]
    result = await Runner.run(agent, task)
    final_output = str(result.final_output)
    return AgentResult(
        agent=normalized,
        summary=final_output,
        findings=[final_output],
    )
