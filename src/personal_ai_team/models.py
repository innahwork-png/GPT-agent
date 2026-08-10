from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    agent: str
    reason: str
    requires_multi_agent: bool = False


class AgentResult(BaseModel):
    agent: str
    summary: str
    findings: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
