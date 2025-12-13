from redis import Redis
from typing import AsyncIterator

class RedisPublisher:
    redis: Redis
    def __init__(self, redis: Redis):
        self.redis = redis

    def publish(self, channel: str, message: bytes) -> None:
        self.redis.publish(channel, message)

class RedisSubscriber:
    redis: Redis

    async def subscribe(self, channel: str) -> AsyncIterator[bytes]:
        sub = self.redis.pubsub()
        await sub.subscribe(channel)

        async for msg in sub.listen():
            if msg["type"] == "message":
                yield msg["data"]

    async def close(self) -> None:
        self.redis.close()