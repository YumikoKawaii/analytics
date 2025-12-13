import redis
from typing import Any, Optional
from app.config import settings
import json

class RedisClient:
    client: redis.Redis
    def __init__(self):
        self._initialize()

    def _initialize(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=settings.redis_decode_responses
        )
        self._test_connection()

    def _test_connection(self) -> None:
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise Exception(f"Failed to connect to Redis: {e}")

    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            raise Exception(f"Failed to get key '{key}': {e}")

    def get_json(self, key: str) -> Optional[dict | list]:
        value = self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        try:
            return self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
        except redis.RedisError as e:
            raise Exception(f"Failed to set key '{key}': {e}")

    def set_json(
        self,
        key: str,
        value: dict | list,
        ex: Optional[int] = None,
        px: Optional[int] = None
    ) -> bool:
        try:
            json_value = json.dumps(value)
            return self.set(key, json_value, ex=ex, px=px)
        except (json.JSONEncodeError, redis.RedisError) as e:
            raise Exception(f"Failed to set JSON key '{key}': {e}")

    def delete(self, *keys: str) -> int:
        try:
            return self.client.delete(*keys)
        except redis.RedisError as e:
            raise Exception(f"Failed to delete keys: {e}")

    def exists(self, *keys: str) -> int:
        try:
            return self.client.exists(*keys)
        except redis.RedisError as e:
            raise Exception(f"Failed to check key existence: {e}")

    def expire(self, key: str, seconds: int) -> bool:
        try:
            return self.client.expire(key, seconds)
        except redis.RedisError as e:
            raise Exception(f"Failed to set expiration for key '{key}': {e}")

    def ttl(self, key: str) -> int:
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            raise Exception(f"Failed to get TTL for key '{key}': {e}")

    def incr(self, key: str, amount: int = 1) -> int:
        try:
            return self.client.incr(key, amount)
        except redis.RedisError as e:
            raise Exception(f"Failed to increment key '{key}': {e}")

    def decr(self, key: str, amount: int = 1) -> int:
        try:
            return self.client.decr(key, amount)
        except redis.RedisError as e:
            raise Exception(f"Failed to decrement key '{key}': {e}")

    def flush_db(self) -> bool:
        try:
            return self.client.flushdb()
        except redis.RedisError as e:
            raise Exception(f"Failed to flush database: {e}")

    def keys(self, pattern: str = "*") -> list[str]:
        try:
            return self.client.keys(pattern)
        except redis.RedisError as e:
            raise Exception(f"Failed to get keys: {e}")

    def ping(self) -> bool:
        try:
            return self.client.ping()
        except redis.RedisError:
            return False

redis_client = RedisClient()
