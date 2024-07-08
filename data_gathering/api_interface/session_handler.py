import asyncio
from aiohttp import ClientSession, ClientResponse
from multiprocessing import Queue as MPQueue
from typing import Callable, Any


class SessionHandler:
    def __init__(
        self, api_queue: MPQueue, result_callback: Callable[[Any], None]
    ) -> None:
        self.api_queue: MPQueue = api_queue
        self.result_callback = (
            result_callback  # TODO: replace with a Callblack class thingy
        )
        self.session: ClientSession | None = None

    async def __aenter__(self):
        await self.start_session()
        return self

    # TODO: figure out how to implement Task Category specific methods for gathering from individual api's.
    # dependency injection is probably the best for this, or make a dictionary for it.
