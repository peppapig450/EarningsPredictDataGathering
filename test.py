import asyncio
import multiprocessing
from aiomultiprocess import Pool
from queue import Full, Empty
import logging
import cProfile


async def async_function(x, queue: multiprocessing.Queue):
    logging.info(f"Starting async task for {x}")
    await asyncio.sleep(0.1)
    data = x * x
    queue.put(data)


def fibonacci(n, max_depth=20):  # Add max_depth parameter
    if n <= 1:
        return n
    elif n > max_depth:
        return fibonacci(max_depth, max_depth) + fibonacci(max_depth - 1, max_depth - 1)
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


def cpu_function(queue: multiprocessing.Queue):
    while True:
        try:
            task = queue.get(timeout=1)
            if task is None:
                break
            result = fibonacci(task)
            print(f"Cpu result: {result}")
        except Full:
            continue


async def main():
    with cProfile.Profile() as pr:
        with multiprocessing.Manager() as manager:
            io_queue = manager.Queue()
            cpu_queue = manager.Queue()
            logger = multiprocessing.log_to_stderr()
            logger.setLevel(logging.INFO)

            for i in range(100):
                io_queue.put_nowait(i)

            with multiprocessing.Pool(processes=6) as cpu_pool:
                cpu_pool.apply_async(cpu_function, args=(cpu_queue,))

                async with Pool(processes=4) as io_pool:
                    while True:
                        try:
                            task = io_queue.get_nowait()
                            await io_pool.apply(
                                async_function, kwds={"x": task, "queue": cpu_queue}
                            )
                        except Empty:
                            break

                cpu_pool.close()
                cpu_pool.join()
        pr.dump_stats("testing-profile.prof")


if __name__ == "__main__":
    asyncio.run(main())
