import logging

from agents import Runner, set_tracing_disabled

from .models import AgentResult
from .sdk_agents import ORCHESTRATOR_AGENT, SPECIALIZED_AGENTS

logger = logging.getLogger("personal_ai_team")

# Tracing is optional; agent execution must not depend on tracing permissions.
set_tracing_disabled(True)


async def run_agent(agent_name: str, task: str) -> AgentResult:
    """Execute one specialized agent directly through the OpenAI Agents SDK."""
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


async def run_orchestrator(task: str) -> AgentResult:
    """Run the central manager; it can call specialist agents as tools and synthesize the final answer."""
    logger.info("Calling OpenAI Agents SDK: agent=orchestrator")
    try:
        result = await Runner.run(ORCHESTRATOR_AGENT, task)
    except Exception:
        logger.exception("OpenAI Agents SDK orchestration failed")
        raise
    final_output = str(result.final_output)
    logger.info("OpenAI Agents SDK orchestration completed")
    return AgentResult(
        agent="orchestrator",
        summary=final_output,
        findings=[final_output],
    )
