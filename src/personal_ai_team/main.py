import hmac
import logging
import os
import uuid

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .memory import MemoryStore
from .orchestrator import Orchestrator

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("personal_ai_team")

app = FastAPI(title="Personal AI Team", version="0.2.3")
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


@app.get("/diagnostics")
def diagnostics(x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)

    # The OpenAI Agents SDK resolves its key from OPENAI_API_KEY.
    openai_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    supabase_configured = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )
    supabase_reachable = False
    supabase_error = None

    if memory.enabled and memory._client is not None:
        try:
            # Bounded read: verifies Data API/database access without returning
            # stored content or any credential.
            memory._client.table("agent_memory").select("id").limit(1).execute()
            supabase_reachable = True
        except Exception as exc:
            supabase_error = type(exc).__name__

    return {
        "status": "ok" if openai_configured and supabase_reachable else "degraded",
        "openai_configured": openai_configured,
        "supabase_configured": supabase_configured,
        "supabase_reachable": supabase_reachable,
        "supabase_error": supabase_error,
        "memory_enabled": memory.enabled,
    }


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
        logger.info("Starting agent run: agent=%s session=%s", orchestrator.route(request.task).agent, session_key)
        memory.save_message(session_key, "user", request.task)
        result = await orchestrator.run_task(request.task)
        memory.save_message(session_key, "assistant", result.summary, result.agent)
        logger.info("Agent run completed: agent=%s session=%s", result.agent, session_key)
        return {**result.model_dump(), "session_key": session_key}
    except ValueError as exc:
        logger.warning("Agent request rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Log the traceback server-side for Railway debugging. Do not expose
        # exception text to the API client because third-party SDK errors can
        # contain request details or other sensitive information.
        logger.exception("Agent execution failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Agent execution failed") from exc


@app.get("/memory")
def get_memory(category: str | None = None, limit: int = 20, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    if not memory.enabled:
        raise HTTPException(status_code=503, detail="Memory is not configured")
    return {"memories": memory.recall(category=category, limit=min(max(limit, 1), 100))}
