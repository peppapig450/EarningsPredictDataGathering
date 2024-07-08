import asyncio
from aiohttp import ClientSession, ClientResponse
from multiprocessing import Queue as MPQueue
from typing import Callable, Any


# TODO: mixin the callback class
class SessionHandler:
    def __init__(
        self, api_queue: MPQueue, result_callback: Callable[[Any], None]
    ) -> None:
        self.api_queue: MPQueue = api_queue
        self.result_callback = result_callback
        self.session: ClientSession | None = None

    async def __aenter__(self):
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close_session()

    async def start_session(self):
        if not self.session:
            self.session = ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def make_api_request(self, )

    # TODO: figure out how to implement Task Category specific methods for gathering from individual api's.
    # dependency injection is probably the best for this, or make a dictionary for it.
