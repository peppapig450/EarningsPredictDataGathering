from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import aiohttp
from typing import Any


class AbstractSessionManager(ABC):
    """
    Abstract base class for managing asynchronous sessions with different APIs.
    """

    def __init__(self) -> None:
        self.session = None

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        pass

    @abstractmethod
    def get_base_url(self) -> str:
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