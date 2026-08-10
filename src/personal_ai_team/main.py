from fastapi import FastAPI
from pydantic import BaseModel

from .orchestrator import Orchestrator

app = FastAPI(title="Personal AI Team", version="0.1.0")
orchestrator = Orchestrator()


class TaskRequest(BaseModel):
    task: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "personal-ai-team"}


@app.get("/agents")
def agents():
    return {"agents": orchestrator.available_agents()}


@app.post("/route")
def route(request: TaskRequest):
    result = orchestrator.route(request.task)
    return {"agent": result.agent, "reason": result.reason}
