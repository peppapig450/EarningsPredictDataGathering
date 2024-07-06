import asyncio
import multiprocessing
from queue import Full, Empty
from typing import Any
import logging
import cProfile

# import fibonacci_solver


async def async_function(x):
    logging.info(f"Starting async task for {x}")
    await asyncio.sleep(0.5)
    return x * x


def fibonacci(n, max_depth=20):  # Add max_depth parameter
    if n <= 1:
        return n
    if n > max_depth:
        return fibonacci(max_depth, max_depth) + fibonacci(max_depth - 1, max_depth - 1)
    return fibonacci(n - 1) + fibonacci(n - 2)


def cpu_function(queue: multiprocessing.Queue, results):
    while True:
        try:
            task = queue.get(timeout=1)
            if task is None:
                break
            # result = fibonacci_solver.fibonacci(task)
            result = fibonacci(task)
            results.append(result)
        except Full:
            continue


async def main():
    with cProfile.Profile() as pr:
        with multiprocessing.Manager() as manager:
            cpu_queue = manager.Queue()
            results = manager.list()
            logger = multiprocessing.log_to_stderr()
            logger.setLevel(logging.INFO)

            tasks = set(range(100))

            with multiprocessing.Pool(processes=6) as cpu_pool:
                cpu_pool.apply_async(cpu_function, args=(cpu_queue, results))

                gatherers = [
                    asyncio.create_task(async_function(task)) for task in tasks
                ]
                for result in gatherers:
                    cpu_queue.put_nowait(await result)

                cpu_pool.close()
                cpu_pool.join()

            # Print results after processing
            for result in results:
                print(f"Fibonacci number: {result}")
        pr.dump_stats("testing-profile.prof")


if __name__ == "__main__":
    asyncio.run(main())
