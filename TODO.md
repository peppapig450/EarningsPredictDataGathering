# TODO

## Actual TODO in program
- [] no longer create a dataframe for each symbol, instead manipulate the dictionaries with list/dictionary comphrension
- [] Rewrite the program to use multiprocessing and asyncio to process data
- [X] mappings directory
- [] use enums
- [] pydantic for verifying content
- [] Improve type hinting and add documentation for gather_all_data and upcoming_earnings_history + any other file
- [] Write tests for those files too
- [] Data verification for python
  - Potentially make sure that stocks gathered by fmpsdk are valid before we loop (Symbols class)
- [X] improve caching so that all the fetch methods in gather_all_data use it
  - Use sqlite and sets, bitwise comparison is fast
- [] Setup <ins>config file reading</ins>
- [] Use alpaca python api (figure out how to get working asynchronously)

## Ideas
- custom JSON decoder for requests/aiohttp

## Research for Data Analysis program
- [] Explore Parquet for data output for time series
- [] Combination of parquet and Sql
- [] Julia, ~~Scala, or Clojure~~ for actual analysis program
