from collections import deque
from multiprocessing import Manager
from multiprocessing import Queue as MPQueue
from multiprocessing.managers import Namespace
from multiprocessing.pool import Pool as _Pool

from . import Task, TaskType


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

    # TODO: look into using imap
    def io_worker(self):
        while not self.io_queue.empty():
            task = self.io_queue.get()
            self.io_pool.apply_async(task.run_io, args=(self.cpu_queue,))

    def cpu_worker(self):
        while not self.cpu_queue.empty():
            task = self.cpu_queue.get()
            task.run_cpu(self.cpu_result_namespace)
