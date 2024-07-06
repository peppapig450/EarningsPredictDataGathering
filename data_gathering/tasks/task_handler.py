from multiprocessing import Queue as MPQueue
from multiprocessing.managers import Namespace
from multiprocessing.pool import Pool as _Pool

from .task_enums import TaskType
from .task_base import Task

# TODO: check ideas.md


# TODO: task handler can't run both io_worker and cpu_worker at once, subclass it and maybe use a proxy
class TaskHandler:
    def __init__(
        self,
        io_pool: _Pool,
        cpu_pool: _Pool,
        io_queue: MPQueue,
        cpu_queue: MPQueue,
        cpu_result_ns: Namespace,
    ):
        self.io_pool: _Pool = io_pool
        self.cpu_pool: _Pool = cpu_pool
        self.io_queue: MPQueue = io_queue
        self.cpu_queue: MPQueue = cpu_queue
        self.cpu_result_namespace: Namespace = cpu_result_ns

    def add_task(self, task: Task):
        if task.task_type == TaskType.IO:
            self.io_queue.put(task)
        elif task.task_type == TaskType.CPU:
            self.cpu_queue.put(task)

    # TODO: figure out how to use the asyncio functionality with the multiprocessing
    def io_worker(self):
        while not self.io_queue.empty():
            task = self.io_queue.get()
            result = self.io_pool.apply(task.run_io)
            self.cpu_queue.put(result)

    def cpu_worker(self):
        while not self.cpu_queue.empty():
            task = self.cpu_queue.get()
            task.run_cpu(self.cpu_result_namespace)
