import os
from typing import Any

import httpx


class InstagramPublisher:
    """Minimal Instagram Graph API publisher for a professional account."""

    def __init__(self) -> None:
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
        self.user_id = os.getenv("INSTAGRAM_USER_ID", "").strip()
        self.base_url = "https://graph.instagram.com"

    @property
    def configured(self) -> bool:
        return bool(self.access_token and self.user_id)

    async def account(self) -> dict[str, Any]:
        if not self.access_token or not self.user_id:
            raise RuntimeError("Instagram publishing is not configured")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/me",
                params={"fields": "id,username", "access_token": self.access_token},
            )
            response.raise_for_status()
            return response.json()

    async def create_reel_container(
        self,
        video_url: str,
        caption: str = "",
        cover_url: str | None = None,
    ) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Instagram publishing is not configured")
        params: dict[str, Any] = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token,
        }
        if cover_url:
            params["cover_url"] = cover_url
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/{self.user_id}/media", params=params)
            response.raise_for_status()
            return response.json()

    async def publish(self, creation_id: str) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Instagram publishing is not configured")
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/{self.user_id}/media_publish",
                params={"creation_id": creation_id, "access_token": self.access_token},
            )
            response.raise_for_status()
            return response.json()

    async def publish_reel(
        self,
        video_url: str,
        caption: str = "",
        cover_url: str | None = None,
    ) -> dict[str, Any]:
        container = await self.create_reel_container(video_url, caption, cover_url)
        creation_id = container.get("id")
        if not creation_id:
            raise RuntimeError("Instagram did not return a media container ID")
        return await self.publish(creation_id)
