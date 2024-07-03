import asyncio
from abc import ABC, abstractmethod
from typing import Any

from data_gathering.utils.safe_uuid import generate_safe_uuid

from .task_enums import DataCategory, RunState, TaskType

type Window = tuple[Any, ...]


class Task(ABC):
    __slots__ = (
        "task_id",
        "task_type",
        "data_category",
        "run_state",
        "io_result",
        "cpu_result",
        "symbols",
        "symbols_seen",
    )

    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory,
        symbols: Window,
        symbols_seen: int,
    ) -> None:
        """
        Initializes a Task instance.

        Args:
            task_type (TaskType): The type of task (IO or CPU bound).
            data_category (DataCategory): The category of data the task handles.
            symbols (Window): A window of symbols related to the task.
            symbols_seen (int): The number of symbols seen.
        """
        self.task_id: str = generate_safe_uuid()
        self.task_type: TaskType = task_type
        self.data_category: DataCategory = data_category
        self.run_state: RunState = RunState.RUN
        self.io_result: Any | None = None
        self.cpu_result: Any | None = None
        self.symbols: Window = symbols
        self.symbols_seen: int = symbols_seen

    @abstractmethod
    async def run_io(self):
        """Abstract method to ensure that all subclasses of Task have a function for IO bound tasks."""

    @abstractmethod
    def run_cpu(self):
        """Abstract method to ensure that all subclasses of Task have a function for CPU bound tasks."""
