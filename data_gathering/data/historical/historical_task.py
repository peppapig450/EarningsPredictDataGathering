from typing import Any
import asyncio
import aiohttp
from .historical_data_session import HistoricalDataSessionManager

from data_gathering.models import DataCategory, Task, TaskMeta, TaskType

from .historical_gathering import HistoricalDataGathering
from .historical_data_session import HistoricalDataSessionManager
from .historical_processing import HistoricalDataProcessing


# TODO: figure out how to create this based on the DataCategory
# task factory method in the TaskHandler is the leader rn or figure out how
# get the proper methods from the data specific classes with the metaclass?
class HistoricalDataTask(Task):
    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory = DataCategory.HISTORICAL,
        symbols: tuple[tuple[Any, ...], int],
        symbols_seen: int
    ) -> None:
        super().__init__(
            task_type=task_type,
            data_category=data_category,
            symbols=symbols,
            symbols_seen=symbols_seen,
        )

    async def _gather_data(
        self, symbols: list[str], session_manager: HistoricalDataSessionManager
    ) -> list[dict[str, Any]]:
        """Gathers data for the specified symbols.

        Args:
            symbols (list[str]): _description_
            session_manager (HistoricalDataSessionManager): _description_
        """
        data_collector = HistoricalDataGathering()
        pass

    def run_io(self):
        pass

    def run_cpu(self):
        pass
