"""Privacy-minimized, best-effort task execution audit in existing Supabase tables."""
import logging
import uuid
from datetime import datetime, timezone

from .projects import route_project

logger = logging.getLogger("personal_ai_team.audit")

def _now():
    return datetime.now(timezone.utc).isoformat()

def start_audit(memory, task: str, source: str):
    """Never store user prompts, answers, session keys or secrets in audit rows."""
    route = route_project(task)
    if not memory.enabled:
        return None
    task_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    try:
        memory._client.table("tasks").insert({
            "id": task_id,
            "task": "[redacted: see authorized conversation store]",
            "status": "running",
            "selected_agent": route.specialist,
            "started_at": _now(),
            "metadata": {"project": route.project, "source": source, "audit_version": 1},
        }).execute()
    except Exception:
        logger.warning("Could not create audit task", exc_info=True)
        return None
    try:
        memory._client.table("agent_runs").insert({
            "id": run_id, "task_id": task_id, "agent": "orchestrator",
            "status": "running", "input": {"project": route.project, "source": source},
        }).execute()
    except Exception:
        logger.warning("Could not create audit run", exc_info=True)
        run_id = None
    return (task_id, run_id)

def finish_audit(memory, audit, success: bool, error: Exception | None = None):
    if not audit or not memory.enabled:
        return
    task_id, run_id = audit
    state = "completed" if success else "failed"
    # Error class only: exception messages can include tokens and private data.
    error_type = type(error).__name__ if error else None
    try:
        memory._client.table("tasks").update({
            "status": state, "completed_at": _now(),
            "error": error_type, "result": {"success": success},
        }).eq("id", task_id).execute()
    except Exception:
        logger.warning("Could not finish audit task", exc_info=True)
    if run_id:
        try:
            memory._client.table("agent_runs").update({
                "status": state, "completed_at": _now(),
                "error": error_type, "output": {"success": success},
            }).eq("id", run_id).execute()
        except Exception:
            logger.warning("Could not finish audit run", exc_info=True)
