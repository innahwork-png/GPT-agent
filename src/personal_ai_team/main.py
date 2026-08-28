import hmac
import logging
import os
import uuid

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from .memory import MemoryStore
from .orchestrator import Orchestrator

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("personal_ai_team")

app = FastAPI(title="Personal AI Team", version="0.3.0")
orchestrator = Orchestrator()
memory = MemoryStore()
web_security = HTTPBasic()


class TaskRequest(BaseModel):
    task: str
    session_key: str | None = None


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


@app.post("/chat")
async def chat(request: TaskRequest, username: str = Depends(require_web_auth)):
    session_key = request.session_key or f"web:{username}:{uuid.uuid4()}"
    try:
        route = orchestrator.route(request.task)
        logger.info("Starting web agent run: agent=%s session=%s", route.agent, session_key)
        memory.save_message(session_key, "user", request.task)
        result = await orchestrator.run_task(request.task)
        memory.save_message(session_key, "assistant", result.summary, result.agent)
        logger.info("Web agent run completed: agent=%s session=%s", result.agent, session_key)
        return {**result.model_dump(), "session_key": session_key}
    except ValueError as exc:
        logger.warning("Web agent request rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Web agent execution failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Agent execution failed") from exc


@app.get("/health")
def health():
    return {"status": "ok", "service": "personal-ai-team", "memory": memory.enabled}


@app.get("/diagnostics")
def diagnostics(x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    openai_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    supabase_configured = bool(os.getenv("SUPABASE_URL", "").strip()) and bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )
    supabase_reachable = False
    supabase_error = None
    if memory.enabled and memory._client is not None:
        try:
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
        logger.exception("Agent execution failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Agent execution failed") from exc


@app.get("/memory")
def get_memory(category: str | None = None, limit: int = 20, x_api_key: str | None = Header(default=None)):
    require_api_token(x_api_key)
    if not memory.enabled:
        raise HTTPException(status_code=503, detail="Memory is not configured")
    return {"memories": memory.recall(category=category, limit=min(max(limit, 1), 100))}
