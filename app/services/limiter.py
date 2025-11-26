import time

import redis.asyncio as redis
from fastapi import HTTPException, Request
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: redis.Redis, rate_limit: int = 10, period: int = 60):
        super().__init__(app)
        self.redis = redis
        self.rate_limit = rate_limit
        self.period = period

    async def dispatch(self, request: Request, call_next):
        excluded_paths = ["/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in excluded_paths):
            return await call_next(request)

        client_ip = request.client.host
        session_id = request.cookies.get("session_id")

        if not session_id:
            return await call_next(request)

        key = f"rate_limit:{client_ip}:{session_id}"
        current_time = int(time.time())

        try:
            await self.redis.zremrangebyscore(key, 0, current_time - self.period)
            request_count = await self.redis.zcard(key)

            if request_count >= self.rate_limit:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                )

            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, self.period)

        except RedisError:
            raise HTTPException(status_code=500, detail="Redis connection error.")
        except Exception:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        return await call_next(request)
