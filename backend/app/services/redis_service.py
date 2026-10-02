import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# In-memory storage fallback
_MEMORY_CACHE: Dict[str, Any] = {}
_MEMORY_EXPIRY: Dict[str, float] = {}
_RATE_LIMIT_BUCKETS: Dict[str, list] = {}

class RedisService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        if redis_url:
            try:
                import redis
                client = redis.from_url(redis_url, decode_responses=True, socket_timeout=1.0)
                client.ping()
                self.redis_client = client
                logger.info("Connected to Redis server.")
            except Exception as e:
                logger.info(f"Redis not available ({e}). Using robust in-memory cache and rate limiter.")
                self.redis_client = None

    def set_workflow_state(self, workflow_id: str, state_dict: Dict[str, Any], expire_seconds: int = 3600) -> None:
        key = f"agent:workflow:{workflow_id}"
        val = json.dumps(state_dict)
        if self.redis_client:
            try:
                self.redis_client.setex(key, expire_seconds, val)
                return
            except Exception:
                pass
        _MEMORY_CACHE[key] = val
        _MEMORY_EXPIRY[key] = time.time() + expire_seconds

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        key = f"agent:workflow:{workflow_id}"
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                pass
        
        # Check memory
        if key in _MEMORY_CACHE:
            if time.time() <= _MEMORY_EXPIRY.get(key, float("inf")):
                return json.loads(_MEMORY_CACHE[key])
            else:
                del _MEMORY_CACHE[key]
                _MEMORY_EXPIRY.pop(key, None)
        return None

    def check_rate_limit(self, identifier: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """
        Token-bucket rate limiter.
        Returns True if request is allowed, False if rate limited.
        """
        now = time.time()
        key = f"ratelimit:{identifier}"

        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.zadd(key, {str(now): now})
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zcard(key)
                pipe.expire(key, window_seconds)
                _, _, count, _ = pipe.execute()
                return count <= max_requests
            except Exception:
                pass

        # In-memory fallback
        timestamps = _RATE_LIMIT_BUCKETS.setdefault(key, [])
        # Evict old
        timestamps = [t for t in timestamps if t > now - window_seconds]
        if len(timestamps) >= max_requests:
            _RATE_LIMIT_BUCKETS[key] = timestamps
            return False
        timestamps.append(now)
        _RATE_LIMIT_BUCKETS[key] = timestamps
        return True

    def cache_get(self, key: str) -> Optional[str]:
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception:
                pass
        if key in _MEMORY_CACHE:
            if time.time() <= _MEMORY_EXPIRY.get(key, float("inf")):
                return str(_MEMORY_CACHE[key])
            else:
                del _MEMORY_CACHE[key]
                _MEMORY_EXPIRY.pop(key, None)
        return None

    def cache_set(self, key: str, value: str, expire_seconds: int = 300) -> None:
        if self.redis_client:
            try:
                self.redis_client.setex(key, expire_seconds, value)
                return
            except Exception:
                pass
        _MEMORY_CACHE[key] = value
        _MEMORY_EXPIRY[key] = time.time() + expire_seconds

from backend.app.core.config import settings
redis_service = RedisService(settings.REDIS_URL)
