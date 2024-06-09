from collections import ChainMap, deque
from multiprocessing import Manager, Pool
from multiprocessing import Queue as MPQueue

from data_gathering.config.api_keys import APIKeys
from data_gathering.data.get_upcoming_earnings import UpcomingEarnings
from data_gathering.models.date_range import DateRange, Unit
from data_gathering.models.symbol_iterator import BatchIteratorWithCount
from data_gathering.models.task import Task, TaskType
from data_gathering.models.task_handler import TaskHandler
from data_gathering.models.task_meta import DataCategory
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache


async def main():
    with Manager() as manager:
        io_queue = MPQueue()
        cpu_queue = MPQueue()
        cpu_result_namespace = manager.Namespace()  # XXX: Use value instead?
        cpu_result_namespace.chainmap = ChainMap()

        api_keys = APIKeys(load_from="config")
        cache = BlacklistSymbolCache()

        upcoming = UpcomingEarnings(api_keys, cache)

        io_pool = Pool(processes=2)
        cpu_pool = Pool(processes=2)

        handler = TaskHandler(
            io_pool, cpu_pool, io_queue, cpu_queue, cpu_result_namespace
        )

        upcoming_dates = DateRange.get_dates(
            init_offset=1,
            date_window=14,
            init_unit=Unit.DAYS,
            date_window_unit=Unit.DAYS,
        )

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
            # sliding window with itertools? or use look ahead for the io queue
            tasks = [
                Task(
                    task_id=1,  # TODO: figure out task id setup ( PID prolly)
                    task_type=TaskType.IO,
                    data_category=current_category,
                    symbols=window,
                    symbols_seen=symbols_iterator.total_seen,
                )
                for window, _ in symbols_iterator
            ]

            for task in tasks:
                handler.add_task(task)
            # other idea:
            #    Create initial tasks for each symbol in the current category
            #    tasks = [Task(task_id=symbol, task_type=TaskType.IO, data_category=current_category, symbols=[symbol]) for symbol in symbols]
            #
            #    Add tasks to the IO queue
            #    for task in tasks:
            #        io_pool.apply_async(task.run_io, callback=lambda result: cpu_queue.put(result))

            # Start io and cpu worker
            handler.io_worker()
            handler.cpu_worker()

        # wait for all tasks to complete
        io_pool.close()
        io_pool.join()
        cpu_pool.close()
        cpu_pool.join()

        # Handle the result namespace
