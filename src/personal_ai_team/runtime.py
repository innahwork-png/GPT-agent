import logging

from agents import Runner, set_tracing_disabled

from .sdk_agents import SPECIALIZED_AGENTS
from .models import AgentResult

logger = logging.getLogger("personal_ai_team")

# Tracing is optional; agent execution must not depend on tracing permissions.
set_tracing_disabled(True)


async def run_agent(agent_name: str, task: str) -> AgentResult:
    """Execute one specialized agent through the OpenAI Agents SDK."""
    normalized = agent_name.strip().lower().replace("-", "_")
    agent = SPECIALIZED_AGENTS[normalized]
    logger.info("Calling OpenAI Agents SDK: agent=%s", normalized)
    try:
        result = await Runner.run(agent, task)
    except Exception:
        logger.exception("OpenAI Agents SDK execution failed: agent=%s", normalized)
        raise
    final_output = str(result.final_output)
    logger.info("OpenAI Agents SDK completed: agent=%s", normalized)
    return AgentResult(
        agent=normalized,
        summary=final_output,
        findings=[final_output],
    )
