from fastapi import HTTPException, Request

from app.core.redis import redis_client

RATE_LIMIT = 20
RATE_PERIOD = 10


async def rate_limit_dependency(request: Request):
    device_id = request.headers.get("X-Device-ID") or request.client.host
    key = f"rate_limit:{device_id}"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, RATE_PERIOD)

    if count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded: Maksimal {RATE_LIMIT} request "
                f"per {RATE_PERIOD} detik."
            ),
        )
