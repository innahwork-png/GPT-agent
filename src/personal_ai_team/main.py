import hmac
import os
import uuid

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .memory import MemoryStore
from .orchestrator import Orchestrator

app = FastAPI(title="Personal AI Team", version="0.2.0")
orchestrator = Orchestrator()
memory = MemoryStore()


class TaskRequest(BaseModel):
    task: str
    session_key: str | None = None


def require_api_token(x_api_key: str | None) -> None:
    expected = os.getenv("AGENT_API_TOKEN", "").strip()
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health():
    return {"status": "ok", "service": "personal-ai-team", "memory": memory.enabled}


@app.get("/agents")
def agents(x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    return {"agents": orchestrator.available_agents()}


@app.post("/route")
def route(request: TaskRequest, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    result = orchestrator.route(request.task)
    return {"agent": result.agent, "reason": result.reason, "requires_multi_agent": result.requires_multi_agent}


@app.post("/run")
async def run(request: TaskRequest, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    session_key = request.session_key or str(uuid.uuid4())
    try:
        memory.save_message(session_key, "user", request.task)
        result = await orchestrator.run_task(request.task)
        memory.save_message(session_key, "assistant", result.summary, result.agent)
        return {**result.model_dump(), "session_key": session_key}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Agent execution failed") from exc


@app.get("/memory")
def get_memory(category: str | None = None, limit: int = 20, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    if not memory.enabled:
        raise HTTPException(status_code=503, detail="Memory is not configured")
    return {"memories": memory.recall(category=category, limit=min(max(limit, 1), 100))}
