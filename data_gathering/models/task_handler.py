from collections import deque
from concurrent.futures import ProcessPoolExecutor
import asyncio
from data_gathering.models.symbol_iterator import SymbolIterator
from data_gathering.models.task_meta import TaskMeta, TaskType, RunState, DataCategory
from data_gathering.models.task import Task


class TaskHandler:
    def __init__(self, io_executor, cpu_executor, symbols):
        self.io_executor = io_executor
        self.cpu_executor = cpu_executor
        self.io_queue = deque()
        self.cpu_queue = deque()  # multi processing queue better
        self.symbols = symbols
        self.categories = deque(DataCategory)
        self.current_category = self.categories[0]

    def add_task(self, task):
        if task.task_type == TaskType.IO:
            self.io_queue.append(task)
        elif task.task_type == TaskType.CPU:
            self.cpu_queue.append(task)

    async def io_worker(self):
        while self.io_queue:
            task = self.io_queue.popleft()
            await task.run_io()
            if task.state == RunState.DONE:
                next_task = task.data_processor_class(
                    id=task.id,
                    io_duration=task.io_duration,
                    task_type=TaskType.CPU,
                    data_category=task.data_category,
                    symbols=task.symbols,
                )
                self.add_task(next_task)

    def cpu_worker(self):
        while self.cpu_queue:
            task = self.cpu_queue.popleft()
            task.run_cpu()
            if task.state == RunState.DONE:
                # CPU processing is done, nothing more to do here for the task
                pass
