# TODO

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

## Ideas
- custom JSON decoder for requests/aiohttp

## Research for Data Analysis program
- [X] Explore Parquet for data output for time series
- [ ] Combination of parquet and Sql
- [ ] Julia, ~~Scala, or Clojure~~ for actual analysis program
