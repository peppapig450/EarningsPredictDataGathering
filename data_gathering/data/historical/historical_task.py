from typing import Any

from data_gathering.models import DataCategory, Task, TaskMeta, TaskType

from .historical_gathering import HistoricalDataGathering
from .historical_data_session import HistoricalDataSessionManager
from .historical_processing import HistoricalDataProcessing


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

    def run_io(self):
