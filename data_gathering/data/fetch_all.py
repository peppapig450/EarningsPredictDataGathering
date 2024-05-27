from multiprocessing import Manager, Queue as MPQueue, Pool
from collections import deque, ChainMap
from data_gathering.models.task_meta import DataCategory
from data_gathering.models.task_handler import TaskHandler
from data_gathering.models.task import Task, TaskType


async def main():
    with Manager() as manager:
        io_queue = MPQueue()
        cpu_queue = MPQueue()
        cpu_result_namespace = manager.Namespace()
        cpu_result_namespace.chainmap = ChainMap()

        io_pool = Pool(processes=2)
        cpu_pool = Pool(processes=2)

        handler = TaskHandler(
            io_pool, cpu_pool, io_queue, cpu_queue, cpu_result_namespace
        )
