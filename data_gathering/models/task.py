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
