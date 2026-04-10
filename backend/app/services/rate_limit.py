from fastapi import HTTPException, status

from app.core.redis import redis_client


def enforce_rate_limit(*, key: str, limit: int, window_seconds: int = 60) -> None:
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window_seconds)
    if current > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Rate limit exceeded')
