import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

    
async def async_function(x, result_queue):
    await asyncio.sleep(1)
    data = x * x
    result_queue.put()



if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        with multiprocessing.Pool(processes=4) as pool:
            