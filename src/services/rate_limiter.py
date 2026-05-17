import logging
import time
from typing import Optional, Tuple

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.config import settings
from src.database import get_redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Redis-based sliding window rate limiter.

    Uses a sorted set to track request timestamps and enforces a maximum number
    of requests within a given time window.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize the rate limiter with a Redis client.

        :param redis_client: Asynchronous Redis client instance.
        """
        self.redis = redis_client

    async def check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
    ) -> Tuple[bool, float]:
        """
        Check if a request is allowed under the rate limit for the given key.

        Implements a sliding window algorithm using a Redis sorted set.
        Returns a tuple (allowed, retry_after_seconds).
            - allowed: True if request is within limit, False otherwise.
            - retry_after_seconds: If not allowed, the number of seconds to wait
              before retrying. 0 if allowed.

        :param key: Unique identifier for the rate limit bucket (e.g., user_id).
        :param max_requests: Maximum number of requests allowed within the window.
        :param window_seconds: Duration of the window in seconds (default 60).
        :return: Tuple of (allowed, retry_after).
        :raises: RedisError on connection or execution failures.
        """
        now = time.time()
        window_start = now - window_seconds

        try:
            # Remove old entries outside the current window
            await self.redis.zremrangebyscore(key, 0, window_start)

            # Count requests in the current window
            request_count = await self.redis.zcard(key)

            if request_count < max_requests:
                # Add current request timestamp to the sorted set
                await self.redis.zadd(key, {str(now): now})

                # Set an expiry on the key to avoid accumulating stale data
                await self.redis.expire(key, window_seconds)

                return (True, 0.0)
            else:
                # Sliding window full: compute retry time based on oldest request
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]  # score = timestamp
                    retry_after = window_seconds - (now - oldest_time)
                    retry_after = max(0.0, retry_after)
                else:
                    retry_after = 0.0
                return (False, retry_after)

        except RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            raise  # Re-raise so caller can handle it