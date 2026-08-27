import hmac
import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .orchestrator import Orchestrator

app = FastAPI(title="Personal AI Team", version="0.1.0")
orchestrator = Orchestrator()


class TaskRequest(BaseModel):
    task: str


def require_api_token(x_api_key: str | None) -> None:
    """Protect application endpoints when AGENT_API_TOKEN is configured."""
    expected = os.getenv("AGENT_API_TOKEN", "").strip()
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health():
    return {"status": "ok", "service": "personal-ai-team"}


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
    try:
        result = await orchestrator.run_task(request.task)
        return result.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Do not expose provider credentials or internal stack traces to clients.
        raise HTTPException(status_code=502, detail="Agent execution failed") from exc
