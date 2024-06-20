import asyncio
import cProfile
import itertools
import json
import logging
import pickle
import re
import datetime
from collections import OrderedDict, defaultdict
from datetime import date
from typing import Optional, Any
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

import aiohttp
import pandas as pd
import requests
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import compute

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.data.get_upcoming_earnings import UpcomingEarnings
from data_gathering.data.historical.historical_data_session import (
    HistoricalDataSessionManager,
)
from data_gathering.models.date_range import DateRange, TimeUnit
from data_gathering.models.mappings import historical_data_mapping
from data_gathering.models.symbol_iterator import BatchIteratorWithCount
from data_gathering.utils.cache.cache_registry import CacheRegistry
from data_gathering.utils.logger_setup import setup_logging
from data_gathering.data.historical.historical_gathering import HistoricalDataGathering


async def gather_data(symbols_batches, api_keys, to_date, session_manager):
    """
    Gathers data for the specified symbols.

    Args:
        symbols_batches (List[List[str]]): The list of batches of stock symbols to gather data for.
        api_keys (str): API keys for authentication.
        to_date (str): The end date for data collection in YYYY-MM-DD format.
        session_manager (HistoricalDataSessionManager): Session manager for handling HTTP sessions.

    Returns:
        List[Dict[str, Any]]: The complete data gathered.
    """
    data_collector = HistoricalDataGathering(
        api_keys, to_date=to_date, session_manager=session_manager
    )
    async with session_manager.manage_session() as session:

        tasks = []
        for batch, _ in symbols_batches:
            # Create a task for each batch of symbol
            tasks.append(
                asyncio.create_task(
                    gather_data_for_batch(batch, session, data_collector)
                )
            )

        # Await the completion of all tasks
        data_results = await asyncio.gather(*tasks)

    # Combine all the results for now
    return data_results


async def gather_data_for_batch(symbols, session, data_collector):
    """
    Gathers data for a batch of symbols.

    Args:
        symbols (List[str]): The list of stock symbols to gather data for.
        session: The aiohttp session to be used for the requests.
        data_collector: The HistoricalDataGathering object for data collection.

    Returns:
        List[Dict[str, Any]]: The complete data gathered for the batch.
    """
    pagination_event = asyncio.Event()

    initial_data, complete_url = await data_collector.make_api_request(
        session, symbols=symbols
    )

    if initial_data.get("next_page_token", None) is not None:
        # If pagination is needed, await the pagination task
        pagination_event.set()

    # Process the initial data
    complete_data = await data_collector.handle_response_pagination(
        session, initial_data, complete_url
    )

    return complete_data


def rename_columns(response_data):
    formatted_data = defaultdict(list)
    for batch in response_data:
        for symbol, data in batch.items():
            for i, bar in enumerate(data):
                renamed_bar = {
                    historical_data_mapping[key]: val
                    for key, val in bar.items()
                    if key in historical_data_mapping
                }
                renamed_bar["symbol"] = symbol
                data[i] = renamed_bar

            formatted_data[symbol] = data

    return formatted_data


def create_dataframes(data_symbols):
    data_list = list(itertools.chain.from_iterable(data_symbols.values()))
    df = pd.DataFrame(data_list)

    if set(["symbol", "timestamp"]).issubset(df.columns):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index(["symbol", "timestamp"], inplace=True)
    return df


async def check_speed(
    symbols_iterator, api_keys, session_manager, to_date="2024-05-04"
):
    complete_data = await gather_data(
        symbols_iterator, api_keys, to_date, session_manager
    )
    with open("output_data.pkl", "wb") as f:
        pickle.dump(complete_data, f)
    return complete_data


async def run_stuff():
    setup_logging()
    api_keys = APIKeys(load_from="config")
    to_date = "2024-05-05"

    cache = CacheRegistry()
    upcoming_dates = DateRange.get_dates(
        init_offset=1,
        date_window=80,
        init_unit=TimeUnit.DAYS,
        date_window_unit=TimeUnit.DAYS,
    )

    upcoming = UpcomingEarnings(api_keys, cache)
    symbols = upcoming.get_upcoming_earnings_list_strings(
        upcoming_dates.from_date, upcoming_dates.to_date
    )
    symbols_iterator = BatchIteratorWithCount(symbols, fraction=0.025)
    session_manager = HistoricalDataSessionManager(api_keys)

    complete_data = await gather_data(
        symbols_iterator, api_keys, to_date, session_manager
    )
    rename_data = rename_columns(complete_data)

    df = create_dataframes(rename_data)
    # df.to_parquet('data.parquet')

    print(df.info(verbose=True))
    print(df.shape)

    # table = pq.read_table('data.parquet', use_pandas_metadata=True)
    # print(table.schema)
    # print(table.slice(0, 5))


if __name__ == "__main__":
    cProfile.run("asyncio.run(run_stuff())", filename="output-async.prof")
