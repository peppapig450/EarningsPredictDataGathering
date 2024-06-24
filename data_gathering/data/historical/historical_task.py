import asyncio
from typing import Any

import aiohttp

from data_gathering.config import APIKeys, Config
from data_gathering.models import DataCategory, Task, TaskType

from .historical_data_session import HistoricalDataSessionManager
from .historical_gathering import HistoricalDataGathering
from .historical_processing import HistoricalDataProcessing

type Symbols = tuple[tuple[Any, ...], int]


class HistoricalDataTask(Task):
    __slots__ = ("_api_keys", "_session_manager", "_from_date", "_to_date")

    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory = DataCategory.HISTORICAL,
        symbols: Symbols,
        symbols_seen: int,
        api_keys: APIKeys,
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

    def _get_gatherer(self):
        if not hasattr(self, "_gatherer"):
            self._gatherer = HistoricalDataGathering(
                api_keys=self._api_keys,
                session_manager=self._session_manager,
                from_date=self._from_date,
                to_date=self._to_date,
            )
        return self._gatherer

    gatherer = property(_get_gatherer)

    def run_io(self, cpu_queue):
        pass

    def run_cpu(self):
        pass

    def _gather_data_for_symbols(self, symbols):
        pass
