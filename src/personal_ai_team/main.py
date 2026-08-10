from fastapi import FastAPI, HTTPException
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
    return {"agent": result.agent, "reason": result.reason, "requires_multi_agent": result.requires_multi_agent}


@app.post("/run")
async def run(request: TaskRequest):
    try:
        result = await orchestrator.run_task(request.task)
        return result.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
