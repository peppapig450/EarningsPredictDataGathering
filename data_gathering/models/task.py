from .task_meta import TaskMeta, RunState, TaskType, DataCategory


class Task(metaclass=TaskMeta):
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
        task_type: TaskType,
        data_category: DataCategory,
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

    # subclass each task type with this class
