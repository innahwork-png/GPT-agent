import os
from typing import Any

from supabase import Client, create_client


class MemoryStore:
    """Small Supabase-backed persistence layer for the personal AI team."""

    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        self._client: Client | None = create_client(url, key) if url and key else None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def save_message(self, session_key: str, role: str, content: str, agent: str | None = None) -> None:
        if not self._client:
            return
        self._client.table("conversations").insert({
            "session_key": session_key,
            "role": role,
            "content": content,
            "agent": agent,
        }).execute()

    def recent_messages(self, session_key: str, limit: int = 12) -> list[dict[str, Any]]:
        if not self._client:
            return []
        result = (
            self._client.table("conversations")
            .select("role,content,agent,created_at")
            .eq("session_key", session_key)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return list(reversed(result.data or []))

    def remember(self, memory_key: str, content: str, category: str = "general", importance: int = 5, metadata: dict[str, Any] | None = None) -> None:
        if not self._client:
            return
        payload = {
            "memory_key": memory_key,
            "content": content,
            "category": category,
            "importance": importance,
            "metadata": metadata or {},
        }
        self._client.table("agent_memory").upsert(payload, on_conflict="memory_key").execute()

    def recall(self, category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if not self._client:
            return []
        query = self._client.table("agent_memory").select("memory_key,content,category,importance,metadata,updated_at").order("importance", desc=True).limit(limit)
        if category:
            query = query.eq("category", category)
        result = query.execute()
        return result.data or []
