from .task_meta import TaskMeta, RunState, TaskType, DataCategory
from abc import ABC, abstractmethod


class Task(ABC, metaclass=TaskMeta):
    __slots__ = [
        "task_id",
        "task_type",
        "data_category",
        "state",
        "io_result",
        "cpu_result",
        "data_processor_class",
        "symbols",
    ]

    def __init__(
        self,
        task_id,
        task_type,
        data_category,
        symbols,
    ) -> None:
        self.task_id = task_id
        self.task_type = task_type
        self.data_category = data_category
        self.state = RunState.RUN
        self.io_result = None
        self.cpu_result = None
        self.data_processor_class = None
        self.symbols = symbols

    @abstractmethod
    async def run_io(self):
        pass

    @abstractmethod
    def run_cpu(self):
        pass
