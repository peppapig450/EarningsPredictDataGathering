import asyncio
from typing import Any

import aiohttp

from data_gathering.models import DataCategory, Task, TaskType

from .historical_data_session import HistoricalDataSessionManager
from .historical_gathering import HistoricalDataGathering
from .historical_processing import HistoricalDataProcessing

type Symbols = tuple[Any, ...]


class HistoricalDataTask(Task):
    __slots__ = ("_api_keys", "_session_manager", "_from_date", "_to_date", "worker")

    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory = DataCategory.HISTORICAL,
        symbols: Symbols,
        symbols_seen: int,
        api_keys,
        session_manager: HistoricalDataSessionManager,
        dates: dict[str, str],
    ) -> None:
        super().__init__(
            task_type=task_type,
            data_category=data_category,
            symbols=symbols,
            symbols_seen=symbols_seen,
        )
        self._api_keys = api_keys
        self._session_manager = session_manager
        self._from_date = dates["from_date"]
        self._to_date = dates["to_date"]

        if task_type == TaskType.IO:
            self.worker = HistoricalDataGathering(
                self._api_keys, self._from_date, self._to_date
            )
        elif task_type == TaskType.CPU:
            # TODO: data processor instantiation
            pass

    def run_io(self, cpu_queue):
        pass

    def run_cpu(self):
        pass

    async def _gather_data_for_symbols(self, symbols: Symbols):
        pagination_event = asyncio.Event()

        async with self._session_manager.manage_session() as session:
            initial_data, complete_url = await self.worker.make_api_request(
                session, symbols
            )
