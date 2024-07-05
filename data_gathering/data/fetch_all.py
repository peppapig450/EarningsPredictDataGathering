from collections import ChainMap, deque
from multiprocessing import Manager, Pool
from multiprocessing import Queue as MPQueue

from data_gathering.config import APIKeys, Config
from data_gathering.data.get_upcoming_earnings import UpcomingEarnings

from data_gathering.models import BatchIteratorWithCount, DateRange
from data_gathering.tasks import TaskCreator, TaskHandler, TaskType, DataCategory
from data_gathering.utils.cache.cache_registry import CacheRegistry


def main():
    with Manager() as manager:
        io_queue = MPQueue()
        cpu_queue = MPQueue()
        # TODO: result queue for io results??
        cpu_result_namespace = manager.Namespace()
        cpu_result_namespace.chainmap = ChainMap()  # TODO: dont use chainmap

        api_keys = APIKeys(load_from="config")
        cache = CacheRegistry()
        config = Config()
        creator = TaskCreator(config)

        upcoming = UpcomingEarnings(api_keys, cache)

        with Pool(processes=2) as io_pool, Pool(processes=2) as cpu_pool:

            handler = TaskHandler(
                io_pool, cpu_pool, io_queue, cpu_queue, cpu_result_namespace
            )

            upcoming_dates_config = config.upcoming_earnings_dates
            upcoming_dates = DateRange.get_dates(**upcoming_dates_config)  # type: ignore

            try:
                symbols = upcoming.get_upcoming_earnings_list_strings(
                    upcoming_dates.from_date, upcoming_dates.to_date
                )
                symbols_iterator = BatchIteratorWithCount(symbols, fraction=0.1)
            except Exception as e:
                exit()  # Not implemented yet

            data_categories = deque(DataCategory)

            while data_categories:
                current_category = data_categories.popleft()

                # Start the initial tasks for each symbol in the current category
                tasks = [
                    creator.create_task(
                        task_type=TaskType.IO,
                        data_category=current_category,
                        symbols=window,
                        symbols_seen=symbols_iterator.total_seen,
                    )
                    for window, _ in symbols_iterator
                ]

                for task in tasks:
                    handler.add_task(task)

                # Start io and cpu worker
                handler.io_worker()
                handler.cpu_worker()

            # wait for all tasks to complete
            io_pool.close()
            io_pool.join()
            cpu_pool.close()
            cpu_pool.join()

            # Handle the result namespace
