from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import aiohttp


class AbstractSessionManager(ABC):
    """
    Abstract base class for managing asynchronous sessions with different APIs.
    """

    def __init__(self) -> None:
        self.session = None

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        pass

    @asynccontextmanager
    async def manage_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.get_headers())
        try:
            yield self.session
        finally:
            if self.session:
                await self.session.close()
                self.session = None
