from typing import Protocol, AsyncIterator


class Publisher(Protocol):
    def publish(self, channel: str, message: bytes) -> None: ...


class Subscriber(Protocol):
    async def subscribe(self, channel: str) -> AsyncIterator[bytes]: ...
    async def close(self) -> None: ...