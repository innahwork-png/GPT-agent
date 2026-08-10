from agents import Agent, Runner


ORCHESTRATOR_INSTRUCTIONS = """
You are the Personal AI Team Orchestrator.
Route work to specialized agents, decompose complex tasks, verify important results,
and require human approval before external side effects such as sending messages,
booking, paying, publishing, deleting, or submitting official forms.
Do not invent facts or credentials.
""".strip()


def build_orchestrator_agent() -> Agent:
    """Create the root SDK agent. Specialized handoffs/tools are added in later phases."""
    return Agent(
        name="Personal AI Team Orchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
    )


async def run_task(task: str):
    """Run a task through the root agent once the cloud runtime has a configured key."""
    agent = build_orchestrator_agent()
    return await Runner.run(agent, task)
