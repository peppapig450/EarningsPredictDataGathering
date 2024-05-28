from .task_meta import DataCategory, RunState, TaskMeta, TaskType
from typing import List, Optional, Any, Sequence
from .upcoming_earning import UpcomingEarning


type Symbols = Sequence[UpcomingEarning | str]


class Task(metaclass=TaskMeta):
    """
    A class representing a task with specific attributes and state.

    Attributes:
        task_id (str): The unique identifier of the task.
        task_type (TaskType): The type of task (IO or CPU bound).
        data_category (DataCategory): The category of data the task handles.
        state (RunState): The current state of the task (RUN or DONE).
        io_result (Optional[Any]): The result of the IO operation, initially None.
        cpu_result (Optional[Any]): The result of the CPU operation, initially None.
        data_processor_class (Optional[str]): The data processor class name, assigned by the metaclass.
        symbols (Symbols): List of symbols related to the task.
    """

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
        *,
        task_id: int,
        task_type: TaskType,
        data_category: DataCategory,
        symbols: Symbols,
    ) -> None:
        """
        Initializes a Task instance.

        Args:
            task_id (int): The unique identifier of the task.
            task_type (TaskType): The type of task (IO or CPU bound).
            data_category (DataCategory): The category of data the task handles.
            symbols (List[UpcomingEarning]): List of symbols related to the task.
        """
        self.task_id: int = task_id
        self.task_type: TaskType = task_type
        self.data_category: DataCategory = data_category
        self.state: RunState = RunState.RUN
        self.io_result: Optional[Any] = None
        self.cpu_result: Optional[Any] = None
        self.symbols: Symbols = symbols

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
