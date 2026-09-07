# Instagram Publishing

The service can publish Reels through Instagram's Graph API using `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID` environment variables.

Required Railway variables:
- `INSTAGRAM_ACCESS_TOKEN` — Instagram User access token; keep secret.
- `INSTAGRAM_USER_ID` — Instagram professional account ID.

The video and optional cover must be publicly reachable URLs. Publishing is intentionally explicit: the application should call the publisher only after content approval.
