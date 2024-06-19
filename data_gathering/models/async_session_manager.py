from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from aiohttp import ClientSession


class AbstractSessionManager(ABC):
    """
    Abstract base class for managing asynchronous sessions with different APIs.
    """

    def __init__(self) -> None:
        self.session: ClientSession | None = None

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        pass

    @asynccontextmanager
    async def manage_session(self) -> AsyncGenerator[ClientSession, Any]:
        if not self.session:
            self.session = ClientSession(headers=self.get_headers())
        try:
            yield self.session
        finally:
            if self.session:
                await self.session.close()
                self.session = None
