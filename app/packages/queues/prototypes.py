from typing import Protocol, Iterator


class Publisher(Protocol):
    def publish(self, channel: str, message: bytes) -> None: ...


class Subscriber(Protocol):
    def subscribe(self, channel: str) -> Iterator[bytes]: ...
    def close(self) -> None: ...