from collections import deque
from multiprocessing import Pool, Queue as MPQueue
from data_gathering.models.task_meta import TaskMeta, TaskType, RunState, DataCategory
from data_gathering.models.task import Task


class TaskHandler:
    def __init__(self, io_pool, cpu_pool, io_queue, cpu_queue, cpu_result_ns):
        self.io_pool = io_pool
        self.cpu_pool = cpu_pool
        self.io_queue = io_queue
        self.cpu_queue = cpu_queue
        self.cpu_result_namespace = cpu_result_ns

    def add_task(self, task):
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
