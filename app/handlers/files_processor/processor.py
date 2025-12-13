from app.packages.queues.prototypes import Subscriber
from app.packages.queues.redis import RedisSubscriber
from app.packages.infrastructure.redis import redis_cli
from app.packages.constants.constants import FILES_TOPIC


class Processor:
    subscriber: Subscriber

    def __init__(self):
        self.subscriber = RedisSubscriber(redis_cli)

    def run(self):
        print(f"Starting processor, subscribing to {FILES_TOPIC}...")
        for message in self.subscriber.subscribe(FILES_TOPIC):
            print(f"Received message: {message}")
