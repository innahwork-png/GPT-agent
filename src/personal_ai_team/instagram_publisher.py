import asyncio
import os
from typing import Any

import httpx


class InstagramPublisher:
    """Instagram Graph API publisher for a professional account."""

    def __init__(self) -> None:
        # Meta access tokens must not contain formatting whitespace. Normalize
        # accidental line breaks/spaces introduced while copying the token.
        self.access_token = "".join(os.getenv("INSTAGRAM_ACCESS_TOKEN", "").split())
        self.user_id = os.getenv("INSTAGRAM_USER_ID", "").strip()
        self.base_url = "https://graph.instagram.com"

    @property
    def configured(self) -> bool:
        return bool(self.access_token and self.user_id)

    async def account(self) -> dict[str, Any]:
        self._require_configured()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/me",
                params={"fields": "id,username", "access_token": self.access_token},
            )
            self._raise_for_meta(response)
            return response.json()

    async def create_reel_container(
        self,
        video_url: str,
        caption: str = "",
        cover_url: str | None = None,
    ) -> dict[str, Any]:
        self._require_configured()
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
            self._raise_for_meta(response)
            return response.json()

    async def container_status(self, creation_id: str) -> dict[str, Any]:
        self._require_configured()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/{creation_id}",
                params={"fields": "status_code,status", "access_token": self.access_token},
            )
            self._raise_for_meta(response)
            return response.json()

    async def wait_until_ready(self, creation_id: str, timeout_seconds: int = 300) -> dict[str, Any]:
        """Wait for Meta to finish processing the uploaded Reel before publishing it."""
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        while True:
            status = await self.container_status(creation_id)
            status_code = str(status.get("status_code", "")).upper()
            if status_code in {"FINISHED", "PUBLISHED"}:
                return status
            if status_code in {"ERROR", "EXPIRED"}:
                raise RuntimeError(f"Instagram media processing failed: {status}")
            if asyncio.get_running_loop().time() >= deadline:
                raise TimeoutError("Instagram media container was not ready within 5 minutes")
            await asyncio.sleep(5)

    async def publish(self, creation_id: str) -> dict[str, Any]:
        self._require_configured()
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/{self.user_id}/media_publish",
                params={"creation_id": creation_id, "access_token": self.access_token},
            )
            self._raise_for_meta(response)
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
        await self.wait_until_ready(creation_id)
        return await self.publish(creation_id)

    def _raise_for_meta(self, response: httpx.Response) -> None:
        if not response.is_error:
            return
        try:
            payload = response.json()
            detail = payload.get("error", payload)
        except ValueError:
            detail = response.text[:1000]
        raise RuntimeError(f"Instagram API {response.status_code}: {detail}")

    def _require_configured(self) -> None:
        if not self.configured:
            raise RuntimeError("Instagram publishing is not configured")