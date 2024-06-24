import importlib
from typing import Any

from data_gathering.data.historical.historical_data_session import (
    HistoricalDataSessionManager,
)
from data_gathering.models import TaskCreationError

from . import DataCategory, TaskType

type Window = tuple[tuple[Any, ...], int]


class TaskCreator:
    def __init__(self, config) -> None:
        self.config = config
        self.api_keys = config.api_keys

    def create_task(
        self,
        task_type: TaskType,
        data_category: DataCategory,
        symbols: Window,
        symbols_seen: int,
    ):
        # TODO: look into using a dataclass for the parameters
        match data_category:
            case DataCategory.HISTORICAL:
                _class = self._get_class_from_category(data_category)
                session_manager = HistoricalDataSessionManager(self.api_keys)
                dates = self.config.historical_gathering_dates
                return _class(
                    task_type=task_type,
                    data_category=data_category,
                    symbols=symbols,
                    symbols_seen=symbols_seen,
                    api_keys=self.api_keys,
                    session_manager=session_manager,
                    dates=dates,
                )
            case _:
                raise TaskCreationError("Something went wrong creating the class")

    def _get_class_from_category(self, data_category: DataCategory):
        module_path = self._get_module_path_from_category(data_category)
        _class = self._get_class_object(module_path)
        return getattr(_class, data_category.value)

    def _get_module_path_from_category(self, data_category: DataCategory):
        module_path = data_category.get_task_class_path(data_category)
        if not module_path:
            raise TaskCreationError(
                f"Something went wrong retrieving the module path from {data_category}"
            )
        return module_path

    def _get_class_object(self, module_path: str):
        parts = module_path.strip(".").split(".")

        package_path = ".".join(parts[:-1])

        try:
            module = importlib.import_module(package_path)
            return module
        except ModuleNotFoundError as e:
            raise TaskCreationError(
                f"Cannot create task, task specific module not found: {package_path}"
            ) from e
