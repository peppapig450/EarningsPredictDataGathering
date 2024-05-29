# TODO

#### Dynamic sleeping calculation
- utilize memoisation here

```python
import time

def calculate_sleep_time(rate_limit, next_limit_change, remaining_requests, buffer_ratio=0.1, window_size=10):
  """
  This function calculates the ideal sleep time to avoid hitting the API rate limit,
  taking into account remaining requests, harmonic moving average processing time, and buffer.

  Args:
      rate_limit: The maximum number of requests allowed per unit time (e.g., per second).
      next_limit_change: The Unix epoch timestamp for the next time the rate limit resets.
      remaining_requests: The number of requests remaining within the current rate limit window.
      buffer_ratio: Optional parameter (default 0.1) representing the buffer percentage to add to the base sleep time.
      window_size: Optional parameter (default 10) representing the size of the window for the harmonic moving average.

  Returns:
      The ideal sleep time in seconds.
  """

  current_time = time.time()
  time_until_reset = next_limit_change - current_time

  # Initialize harmonic mean with a small value to avoid division by zero
  harmonic_mean = 0.01

  # Track processing times for harmonic mean calculation
  processing_times = []

  def update_harmonic_mean(processing_time):
    """
    Updates the harmonic mean with a new processing time.
    """
    nonlocal harmonic_mean  # Modify the variable in the enclosing scope
    if len(processing_times) < window_size:
      processing_times.append(processing_time)
    else:
      # Remove the oldest processing time from the window
      oldest_time = processing_times.pop(0)
      harmonic_mean -= 1 / oldest_time

    # Add the new processing time
    processing_times.append(processing_time)
    harmonic_mean += 1 / processing_time

    # Calculate the harmonic mean using the window elements
    harmonic_mean = window_size / harmonic_mean

  # Update harmonic mean for each request (replace with your logic to record processing time)
  # You'll need to call this function after each request completes to update the processing_times list

  # Ideal sleep time per request considering remaining requests and harmonic mean
  ideal_sleep_per_request = min(time_until_reset / remaining_requests, time_until_reset / (rate_limit + harmonic_mean))

  # Ensure sleep time per request is non-negative
  sleep_per_request = max(0, ideal_sleep_per_request)

  # Apply buffer to sleep time per request
  sleep_time = sleep_per_request * (1 + buffer_ratio)

  return max(0, sleep_time)  # Ensure overall sleep time is non-negative
```

## Actual TODO in program:

- [ ] Figure out the most optimial way to handle the concurrent gathering and processing (figure out how to use Queues, maybe change_executor with async, threadpool, shared manager, task groups)
- [ ] Figure out how to use the returned headers for rate limiting


- [X] no longer create a dataframe for each symbol, instead manipulate the dictionaries with list/dictionary comphrension
- [X] mappings directory
- [ ] use enums ?
- [ ] pydantic for verifying content

- [ ] Improve type hinting and add documentation for gather_all_data and upcoming_earnings_history + any other file
- [ ] Write tests for those files too
- [X] improve caching so that all the fetch methods in gather_all_data use it
  - Use sqlite and sets, bitwise comparison is fast
- [ ] Setup <ins>config file reading</ins>
- [X] Use alpaca python api (figure out how to get working asynchronously)

### Concurrency:
- Use 2 queues, one for gathering , one for processing
- Use Symbol class with properties for each data type, along with slots
- Look into context managers

## Ideas
- custom JSON decoder for requests/aiohttp

## Research for Data Analysis program
- [X] Explore Parquet for data output for time series
- [ ] Combination of parquet and Sql
- [ ] Julia, ~~Scala, or Clojure~~ for actual analysis program
