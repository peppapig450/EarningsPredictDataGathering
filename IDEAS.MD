# Ideas

## Global Sleeping and maximum efficiency
- Change from using 1 manager for both process pools to using a central broker that holds two seperate managers

- if sleep is neeeded, increase the rate at which we send data to the processing queue to minimize time we're doing nothing.

## like this

### Improved Multiprocessing Structure with Sub-Managers

This approach utilizes a top-level manager process and sub-managers for I/O and CPU tasks to enhance code organization and communication within your multi-process system.

**1. Top-Level Manager:**

- Create a top-level manager process using `multiprocessing.Manager()`.
- Within this manager:
    - Create two sub-managers using the `Manager.dict()` method.
        - One sub-manager for I/O tasks (holding the `io_queue`).
        - Another sub-manager for CPU tasks (holding the `cpu_queue` and `cpu_result_namespace`).

**2. Sub-Managers:**

- Each sub-manager inherits from a custom `SubManager` class you define.
- The `SubManager` class can have attributes for the associated queue and additional data structures (if needed) specific to I/O or CPU tasks.

**3. Worker Processes:**

- Modify your worker process logic to access the relevant sub-manager based on their task type (I/O or CPU).

**Worker Process Logic:**

  * **I/O Workers:**
      - Use the sub-manager associated with the I/O queue to:
          - Put tasks onto the `io_queue`.
          - Potentially retrieve results from the CPU sub-manager (if applicable).
  * **CPU Workers:**
      - Use the sub-manager associated with the CPU queue and namespace to:
          - Get tasks from the `cpu_queue`.
          - Store results in the `cpu_result_namespace`.

**Benefits:**

- Improved code organization and separation of concerns for I/O and CPU tasks.
- Potential for adding more sub-managers for additional task types in the future.
- Centralized management of queues and results under the top-level manager.

**Drawbacks:**

- Introduces an additional layer of abstraction with sub-managers.
- Requires careful design of the `SubManager` class to handle specific task needs.

**Example Structure (without error handling or logging):**

```python
from multiprocessing import Manager

class SubManager:
    def __init__(self, manager, queue_name, result_namespace=None):
        self.manager = manager
        self.queue = manager.dict()[queue_name]
        if result_namespace:
            self.result_namespace = result_namespace

# Top-level manager process
with Manager() as manager:
    io_sub_manager = SubManager(manager, "io_queue")
    cpu_sub_manager = SubManager(manager, "cpu_queue", manager.Namespace())
    cpu_sub_manager.result_namespace.chainmap = ChainMap()

    # ... rest of your code using io_sub_manager and cpu_sub_manager ...
```

**Use this code with caution and adapt it to your specific needs.**

**Important Note:**
While this example provides a basic structure, remember to implement error handling, logging, and synchronization mechanisms (e.g., locks) within the sub-managers to ensure data consistency when multiple processes access the queues and namespace concurrently.


## Task switching
if a data gathering task needs to sleep to avoid overwhelming the api

automatically switch to another task that uses a different api

## Use Kafka to stream the parquet to the julia analysis

## Instead of printing out each pagination, once pagination is done print out the number of times we paginated
Like this
```text
Batch {number} processed.
Paginated {number times}.
```

## Passing data from the io queue for gathering data and the cpu queue for processing it.
Possibly use streaming to pass to the queue as its available.

```python
from aiohttp import ClientSession
from multiprocessing import Pool, pool

async def download_chunk(url, chunk_size, queue):
  async with ClientSession() as session:
    async with session.get(url) as response:
      response.raise_for_status()  # Raise exception for non-200 status codes
      async for chunk in response.content.iter_chunked(chunk_size):
        queue.put(chunk)  # Add data chunk to the queue

def process_chunk(chunk):
  # Process the downloaded chunk (e.g., print it)
  print(f"Received chunk: {chunk[:20]}...")  # Print first 20 bytes

if __name__ == "__main__":
  # Download URL and chunk size
  download_url = "https://example.com/large_file.txt"
  chunk_size = 1024

  # Create a pool of worker processes
  with Pool(processes=4) as pool:
    # Initialize a queue
    queue = pool.Queue()

    # Start downloading asynchronously
    download_task = pool.apply_async(download_chunk, args=(download_url, chunk_size, queue))

    # Process downloaded chunks
    while True:
      try:
        chunk = queue.get(timeout=1)  # Set a timeout to avoid infinite wait
        process_chunk(chunk)
      except pool.TimeoutExpired:
        # No data received in the specified timeout, potentially finished downloading
        if download_task.successful():
          print("Download completed!")
        else:
          print("Download failed!")
        break
```

## Combine task creator factory with Task Handler
```python
class TaskHandler:
  def __init__(self, factory):
    self.factory = factory
    self.io_queue = Queue()  # Queue for IO tasks
    self.cpu_queue = Queue()  # Queue for CPU tasks

  def create_task(self, task_type, **kwargs):
    task = self.factory.create_task(task_type, **kwargs)
    if isinstance(task, IOTask):
      self.io_queue.put(task)
    elif isinstance(task, CPUTask):
      self.cpu_queue.put(task)
    else:
      raise ValueError(f"Invalid task type: {task_type}")

  def run_tasks(self, num_threads=1):
    # Use threads or other mechanisms to execute tasks concurrently
    # (implementation omitted for brevity)
    for _ in range(num_threads):
      thread = Thread(target=self.execute_task)
      thread.start()
    # Wait for all threads to finish
    for thread in threading.enumerate():
      thread.join()

  def execute_task(self):
    while True:
      # Get task from a queue (implementation omitted for brevity)
      task = get_task_from_queue()
      if task is None:
        break  # No more tasks in queue
      task.run()
      # Handle task result (implementation omitted for brevity)

  # Additional methods for handling results, errors, etc.
```