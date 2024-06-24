import asyncio
from typing import Any

import aiohttp

from data_gathering.config import APIKeys
from data_gathering.models import DataCategory, Task, TaskType

from .historical_data_session import HistoricalDataSessionManager
from .historical_gathering import HistoricalDataGathering
from .historical_processing import HistoricalDataProcessing

type Symbols = tuple[tuple[Any, ...], int]


class HistoricalDataTask(Task):
    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory = DataCategory.HISTORICAL,
        symbols: Symbols,
        symbols_seen: int,
        api_keys: APIKeys,
        session_manager: HistoricalDataSessionManager,
    ) -> None:
        super().__init__(
            task_type=task_type,
            data_category=data_category,
            symbols=symbols,
            symbols_seen=symbols_seen,
        )
        self.api_keys = api_keys
        self.session_manager = session_manager

    def run_io(self):
        pass

    def run_cpu(self):
        pass
