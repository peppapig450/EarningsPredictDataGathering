from typing import Any, Optional

from .task_meta import DataCategory, RunState, TaskMeta, TaskType
from data_gathering.utils.safe_uuid import generate_safe_uuid

type Window = tuple[tuple[Any, ...], int]


class Task(metaclass=TaskMeta):
    """
    A class representing a task with specific attributes and state.

    Attributes:
        task_id (str): The unique identifier of the task, generated using a safe UUID.
        task_type (TaskType): The type of task (IO or CPU bound).
        data_category (DataCategory): The category of data the task handles.
        state (RunState): The current state of the task (RUN or DONE).
        io_result (Optional[Any]): The result of the IO operation, initially None.
        cpu_result (Optional[Any]): The result of the CPU operation, initially None.
        data_category_class (Optional[str]): The data category class name, assigned by the metaclass.
        symbols (Symbols): A window of symbols related to the task.
        symbols_seen (int): The number of symbols seen.

    Note:
        The `task_id` is automatically generated using a safe UUID to ensure uniqueness across
        multiple processes. This ensures each task has a unique identifier without the risk of collisions.
    """

    __slots__ = [
        "task_id",
        "task_type",
        "data_category",
        "state",
        "io_result",
        "cpu_result",
        "data_category_class",
        "symbols",
        "symbols_seen",
    ]

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
        self.state: RunState = RunState.RUN
        self.io_result: Optional[Any] = None
        self.cpu_result: Optional[Any] = None
        self.symbols: Window = symbols
        self.symbols_seen: int = symbols_seen

    # subclass each task type with this class
    """
    example:
        async def run_io(self, result_queue):
            await asyncio.sleep(self.io_duration)
            self.io_result = f"IO result for {self.symbols} in HistoricalTask"
            self.state = RunState.DONE
            result_queue.put(self)

        def run_cpu(self, cpu_result_ns):
            self.cpu_result = f"CPU result for {self.symbols} with {self.io_result}"
            self.state = RunState.DONE
            cpu_result_ns.chainmap[self.id] = self.cpu_result
    """
