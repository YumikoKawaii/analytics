from redis import Redis
from typing import Iterator

class RedisPublisher:
    redis: Redis
    def __init__(self, redis: Redis):
        self.redis = redis

    def publish(self, channel: str, message: bytes) -> None:
        self.redis.publish(channel, message)

class RedisSubscriber:
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    def subscribe(self, channel: str) -> Iterator[bytes]:
        pubsub = self.redis.pubsub()
        pubsub.subscribe(channel)

        for msg in pubsub.listen():
            if msg["type"] == "message":
                yield msg["data"]

    def close(self) -> None:
        self.redis.close()