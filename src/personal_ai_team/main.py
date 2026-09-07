import hashlib
import hmac
import logging
import os
import re
import uuid

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from openai import OpenAI
from pydantic import BaseModel

from .memory import MemoryStore
from .orchestrator import Orchestrator
from .instagram_publisher import InstagramPublisher

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("personal_ai_team")

app = FastAPI(title="Personal AI Team", version="0.5.0")
orchestrator = Orchestrator()
memory = MemoryStore()
web_security = HTTPBasic()
instagram = InstagramPublisher()


class TaskRequest(BaseModel):
    task: str
    session_key: str | None = None


class InstagramPublishRequest(BaseModel):
    video_url: str
    caption: str = ""
    cover_url: str | None = None


def require_api_token(x_api_key: str | None) -> None:
    expected = os.getenv("AGENT_API_TOKEN", "").strip()
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def require_web_auth(credentials: HTTPBasicCredentials = Depends(web_security)) -> str:
    username = os.getenv("WEB_USERNAME", "").strip()
    password = os.getenv("WEB_PASSWORD", "")
    if not username or not password:
        raise HTTPException(status_code=503, detail="Web authentication is not configured")
    valid_user = hmac.compare_digest(credentials.username, username)
    valid_password = hmac.compare_digest(credentials.password, password)
    if not (valid_user and valid_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})
    return username


def extract_explicit_memory(task: str) -> str | None:
    """Extract a clear user instruction to persist a memory item."""
    patterns = (
        r"(?:запомни|запомните|сохрани|сохраняй)\s*[,\-:]?\s*(?:что\s+)?(.+)$",
        r"(?:remember|save)\s+(?:that\s+)?(.+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, task.strip(), flags=re.IGNORECASE | re.DOTALL)
        if match:
            content = re.sub(r"\s+", " ", match.group(1)).strip(" .!?\n\t")
            if content:
                return content
    return None


def memory_context(session_key: str) -> str:
    """Build compact context from persistent memories and recent conversation."""
    sections: list[str] = []
    try:
        memories = memory.recall(limit=20)
        if memories:
            lines = [
                f"- {item.get('content', '').strip()}"
                for item in memories
                if str(item.get("content", "")).strip()
            ]
            if lines:
                sections.append("Persistent user memories:\n" + "\n".join(lines))
    except Exception:
        logger.exception("Persistent memory recall failed")

    try:
        recent = memory.recent_messages(session_key, limit=12)
        if recent:
            lines = []
            for item in recent:
                role = str(item.get("role", "")).strip() or "unknown"
                content = str(item.get("content", "")).strip()
                if content:
                    lines.append(f"{role}: {content}")
            if lines:
                sections.append("Recent conversation context:\n" + "\n".join(lines))
    except Exception:
        logger.exception("Conversation history recall failed")

    if not sections:
        return ""
    return (
        "\n\n[PRIVATE MEMORY CONTEXT — use this as context for the current request. "
        "Do not invent memories and do not reveal internal memory mechanics unless asked.]\n"
        + "\n\n".join(sections)
        + "\n[END PRIVATE MEMORY CONTEXT]\n"
    )


def prepare_task(task: str, session_key: str, username: str) -> str:
    explicit_memory = extract_explicit_memory(task)
    if explicit_memory and memory.enabled:
        memory_key = "user:" + hashlib.sha256(
            f"{username}:{explicit_memory}".encode("utf-8")
        ).hexdigest()
        try:
            memory.remember(
                memory_key=memory_key,
                content=explicit_memory,
                category="user_preference",
                importance=8,
                metadata={"source": "explicit_user_request"},
            )
            logger.info("Persisted explicit user memory: key=%s", memory_key)
        except Exception:
            logger.exception("Failed to persist explicit user memory")

    context = memory_context(session_key)
    if not context:
        return task
    return f"{context}\n\nCurrent user request:\n{task}"


@app.get("/", response_class=HTMLResponse)
def web_chat(_: str = Depends(require_web_auth)):
    return HTMLResponse("""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Personal AI Team</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#f6f7f9;color:#171717}
.card{background:white;border-radius:18px;padding:20px;box-shadow:0 4px 24px #00000012}
h1{margin-top:0}.sub{color:#666}.messages{min-height:360px;max-height:60vh;overflow:auto;margin:20px 0;padding:8px}
.msg{padding:12px 14px;border-radius:14px;margin:10px 0;white-space:pre-wrap}.user{background:#e9f2ff;margin-left:15%}.assistant{background:#f0f0f0;margin-right:15%}
form{display:flex;gap:10px}textarea{flex:1;resize:vertical;min-height:52px;border:1px solid #ddd;border-radius:12px;padding:12px;font:inherit}button{border:0;border-radius:12px;padding:0 20px;font-weight:600;cursor:pointer}
.status{font-size:13px;color:#777;margin-top:10px}
</style>
</head>
<body>
<div class="card">
<h1>Personal AI Team</h1>
<div class="sub">Your private cloud agent</div>
<div id="messages" class="messages"></div>
<form id="form"><textarea id="input" placeholder="Напиши задачу агенту…" required></textarea><button>Send</button></form>
<div id="status" class="status"></div>
</div>
<script>
const form=document.getElementById('form'), input=document.getElementById('input'), messages=document.getElementById('messages'), status=document.getElementById('status');
let sessionKey=localStorage.getItem('personal_ai_session')||crypto.randomUUID(); localStorage.setItem('personal_ai_session',sessionKey);
function add(role,text){const el=document.createElement('div');el.className='msg '+role;el.textContent=text;messages.appendChild(el);messages.scrollTop=messages.scrollHeight;}
form.addEventListener('submit',async e=>{e.preventDefault();const task=input.value.trim();if(!task)return;add('user',task);input.value='';status.textContent='Thinking…';try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task,session_key:sessionKey})});const data=await r.json();if(!r.ok)throw new Error(data.detail||'Request failed');sessionKey=data.session_key;localStorage.setItem('personal_ai_session',sessionKey);add('assistant',data.summary||JSON.stringify(data));status.textContent=data.agent?'Agent: '+data.agent:'';}catch(err){add('assistant','Ошибка: '+err.message);status.textContent='';}});
</script>
</body>
</html>
""")


def safe_error_detail(exc: Exception) -> str:
    message = " ".join(str(exc).split())
    if not message:
        return type(exc).__name__
    for secret_name in ("OPENAI_API_KEY", "AGENT_API_TOKEN", "SUPABASE_SERVICE_ROLE_KEY", "WEB_PASSWORD", "INSTAGRAM_ACCESS_TOKEN"):
        value = os.getenv(secret_name, "")
        if value:
            message = message.replace(value, "[REDACTED]")
    return f"{type(exc).__name__}: {message[:800]}"


def check_openai() -> tuple[bool, str | None]:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return False, "OPENAI_API_KEY is not configured"
    model = os.getenv("OPENAI_MODEL", "gpt-5.6").strip() or "gpt-5.6"
    try:
        OpenAI().models.retrieve(model)
        return True, None
    except Exception as exc:
        return False, safe_error_detail(exc)


@app.post("/chat")
async def chat(request: TaskRequest, username: str = Depends(require_web_auth)):
    session_key = request.session_key or f"web:{username}:{uuid.uuid4()}"
    try:
        route = orchestrator.route(request.task)
        logger.info("Starting web agent run: agent=%s session=%s", route.agent, session_key)
        memory.save_message(session_key, "user", request.task)
        task_with_context = prepare_task(request.task, session_key, username)
        result = await orchestrator.run_task(task_with_context)
        memory.save_message(session_key, "assistant", result.summary, result.agent)
        logger.info("Web agent run completed: agent=%s session=%s", result.agent, session_key)
        return {**result.model_dump(), "session_key": session_key}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        detail = safe_error_detail(exc)
        logger.exception("Web agent execution failed: %s", detail)
        raise HTTPException(status_code=502, detail=detail) from exc


@app.get("/instagram/account")
async def instagram_account():
    """Verify Instagram API access without exposing or requiring any secret in the browser."""
    try:
        account = await instagram.account()
        return {"status": "ok", "account": account}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        detail = safe_error_detail(exc)
        logger.exception("Instagram account check failed: %s", detail)
        raise HTTPException(status_code=502, detail=detail) from exc


@app.post("/instagram/publish")
async def publish_instagram_reel(
    request: InstagramPublishRequest,
    x_api_key: str | None = Header(default=None),
):
    """Explicitly publish an approved Reel to Dancing Camilla's Instagram account."""
    require_api_token(x_api_key)
    try:
        result = await instagram.publish_reel(
            video_url=request.video_url,
            caption=request.caption,
            cover_url=request.cover_url,
        )
        return {"status": "published", **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        detail = safe_error_detail(exc)
        logger.exception("Instagram publication failed: %s", detail)
        raise HTTPException(status_code=502, detail=detail) from exc


@app.get("/health")
def health():
    return {"status": "ok", "service": "personal-ai-team", "memory": memory.enabled}


@app.get("/diagnostics")
def diagnostics():
    """Safe public diagnostic endpoint: exposes status only, never secrets."""
    openai_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    openai_reachable, openai_error = check_openai()
    configured_model = os.getenv("OPENAI_MODEL", "gpt-5.6").strip() or "gpt-5.6"

    supabase_configured = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )
    supabase_reachable = False
    supabase_error = None
    agent_memory_reachable = False
    agent_memory_error = None
    if memory.enabled and memory._client is not None:
        try:
            memory._client.table("conversations").select("role").limit(1).execute()
            supabase_reachable = True
        except Exception as exc:
            supabase_error = type(exc).__name__
        try:
            memory._client.table("agent_memory").select("memory_key").limit(1).execute()
            agent_memory_reachable = True
        except Exception as exc:
            agent_memory_error = type(exc).__name__

    google_drive_configured = all(
        os.getenv(name, "").strip()
        for name in ("GOOGLE_DRIVE_CLIENT_ID", "GOOGLE_DRIVE_CLIENT_SECRET", "GOOGLE_DRIVE_REDIRECT_URI")
    )

    overall_ok = openai_reachable and (not supabase_configured or supabase_reachable)
    return {
        "status": "ok" if overall_ok else "degraded",
        "openai_configured": openai_configured,
        "openai_reachable": openai_reachable,
        "openai_error": openai_error,
        "openai_model": configured_model,
        "supabase_configured": supabase_configured,
        "supabase_reachable": supabase_reachable,
        "supabase_error": supabase_error,
        "agent_memory_reachable": agent_memory_reachable,
        "agent_memory_error": agent_memory_error,
        "google_drive_configured": google_drive_configured,
        "instagram_configured": instagram.configured,
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
        task_with_context = prepare_task(request.task, session_key, "api")
        result = await orchestrator.run_task(task_with_context)
        memory.save_message(session_key, "assistant", result.summary, result.agent)
        logger.info("Agent run completed: agent=%s session=%s", result.agent, session_key)
        return {**result.model_dump(), "session_key": session_key}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        detail = safe_error_detail(exc)
        logger.exception("Agent execution failed: %s", detail)
        raise HTTPException(status_code=502, detail=detail) from exc


@app.get("/memory")
def get_memory(category: str | None = None, limit: int = 20, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    if not memory.enabled:
        raise HTTPException(status_code=503, detail="Memory is not configured")
    return {"memories": memory.recall(category=category, limit=min(max(limit, 1), 100))}
