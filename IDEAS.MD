# Ideas

## Global Sleeping and maximum efficiency
- Change from using 1 manager for both process pools to using a central broker that holds two seperate managers

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
