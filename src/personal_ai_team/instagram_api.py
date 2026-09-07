from typing import Any

from .instagram_publisher import InstagramPublisher


async def publish_instagram_reel(
    video_url: str,
    caption: str = "",
    cover_url: str | None = None,
) -> dict[str, Any]:
    """Publish a publicly reachable MP4/MOV Reel to Instagram."""
    publisher = InstagramPublisher()
    return await publisher.publish_reel(video_url, caption, cover_url)
