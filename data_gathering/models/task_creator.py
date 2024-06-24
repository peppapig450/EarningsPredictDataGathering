import importlib
from typing import Any

from data_gathering.config import APIKeys, Config
from data_gathering.data.historical.historical_task import HistoricalDataTask
from data_gathering.models import TaskCreationError

from . import DataCategory, Task, TaskType

type Window = tuple[tuple[Any, ...], int]


class TaskCreator:
    # TODO: one function to create the class based on the data category (factory class)
    def __init__(self, config: Config) -> None:
        self.config = config
        self.api_keys: APIKeys = config.api_keys

    def create_task(
        self,
        task_type: TaskType,
        data_category: DataCategory,
        symbols: Window,
        symbols_seen: int,
    ):
        match data_category:
            case DataCategory.HISTORICAL:
                _class = self._get_class_from_category(data_category)
                return _class(
                    task_type, data_category, symbols, symbols_seen, self.api_keys
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
