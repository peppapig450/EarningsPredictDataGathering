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
from data_gathering.data.historical.historical_data_session import \
    HistoricalDataSessionManager
from data_gathering.models.date_range import DateRange, Unit
from data_gathering.models.mappings import historical_data_mapping
from data_gathering.models.symbol_iterator import BatchIteratorWithCount
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache
from data_gathering.utils.logger_setup import setup_logging


class HistoricalDataGathering:
    def __init__(
        self,
        api_keys: APIKeys,
        to_date: str,
        cache: BlacklistSymbolCache,
        session_manager: HistoricalDataSessionManager,
        from_date: str = "1983-01-01",

    ) -> None:
        self._apca_key_id, self._apca_api_secret_key = api_keys.get_key(
            APIService.ALPACA
        )
        self.from_date, self.to_date = self._validate_and_init_dates(from_date, to_date)
        self.cache: BlacklistSymbolCache = cache
        self.session_manager: HistoricalDataSessionManager = (
            session_manager  # created by task handler
        )
        self.logger = logging.getLogger(__name__)

    def _validate_and_init_dates(self, from_date: str, to_date: str) -> tuple[str, str]:
        """
        Validates the date strings and initializes the from_date and to_date attributes.

        Args:
            from_date (str): The start date for data collection in YYYY-MM-DD format.
            to_date (str): The end date for data collection in YYYY-MM-DD format.

        Returns:
            Tuple[str, str]: A tuple containing the validated from_date and to_date.

        Raises:
            ValueError: If the date strings do not match the YYYY-MM-DD format.
        """
        compiled_pattern = re.compile(r"^\d{4}\-(0?[1-9]|1[0-2])\-(0?[1-9]|[12][0-9]|3[01])$")

        if not compiled_pattern.match(from_date):
            raise ValueError(f"Invalid date string for from_date: {from_date}. Use YYYY-MM-DD format.")

        if not compiled_pattern.match(to_date):
            raise ValueError(f"Invalid date string for to_date: {to_date}. Use YYYY-MM-DD format. ")

        return from_date, to_date


    def get_headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self._apca_key_id,
            "APCA-API-SECRET-KEY": self._apca_api_secret_key,
        }

    async def get_data(self, symbols):
        symbols_batch = ",".join(symbols)
        encoded_symbols = quote(symbols_batch)
        base_url: str = "https://data.alpaca.markets/v2/stocks/bars"
        rest_of_url: str = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}"
        complete_url: str = f"{base_url}?symbols={encoded_symbols}{rest_of_url}"

        async with self.session_manager.manage_session() as session:
            async with session.get(complete_url) as response:
                data_dict = await response.json()
                return data_dict

    async def make_api_request(self, session, symbols: Optional[list[str]] = None, url: Optional[str] = None) -> tuple[dict[str, Any], str]:
        """
        Makes an API request to the Alpaca service.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to be used for the request.
            symbols (Optional[List[str]]): A list of stock symbols to gather data for.
            url (Optional[str]): A complete URL to gather data from.

        Returns:
            Tuple[Dict[str, Any], str]: The response data and the complete URL.

        Raises:
            ValueError: If neither symbols nor a URL are provided.
            RuntimeError: If there is an error gathering data.
        """
        if symbols is not None:
            symbols_batch = ",".join(symbols)
            encoded_symbols = quote(symbols_batch)
            base_url: str = "https://data.alpaca.markets/v2/stocks/bars"
            rest_of_url: str = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&asof={date.today().strftime("%Y-%m-%d")}&feed=sip&sort=asc"
            complete_url: str = f"{base_url}?symbols={encoded_symbols}{rest_of_url}"
        elif url is not None:
            complete_url = url
        else:
            raise ValueError("Neither symbols batch nor a url passed.")

        try:
            async with session.get(complete_url) as response:
                data = await response.json()
                return data, complete_url
        except aiohttp.ClientConnectionError as err:
            self.logger.error(f"Error: {err} - occured while retrieving data from {complete_url}", exc_info=True)
        except aiohttp.ClientResponseError as err:
            self.logger.error(f"Error: {err} - occured while retrieving data from {complete_url}", exc_info=True)

    async def handle_response_pagination(self, session, data, url: str):
        """
        Handles the pagination for API responses.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to be used for the requests.
            data (Dict[str, Any]): The initial response data.
            url (str): The complete URL for the request.

        Returns:
            OrderedDict: The complete data gathered from all pages.
        """
        data_dict = OrderedDict()
        if data and url:
            data_dict.update(data.get("bars", None))
            next_page_token = data.get("next_page_token", None)

            while next_page_token:
                self.logger.debug(f"Getting pagination for {url} with {next_page_token}")

                # Parse the url
                parsed_url = urlparse(url)
                query_params = parse_qsl(parsed_url.query) # split the query

                # Insert the 'next_page_token' before the 'sort parameter
                for i, (key, value) in enumerate(query_params):
                    if key == "sort":
                        query_params.insert(i, ("page_token", next_page_token))
                        break
                else:
                    # If 'sort' parameter not found, append the 'next_page_token' at the end
                    query_params.append(("page_token", next_page_token))

                # Encode the next query params
                new_query = urlencode(query_params, doseq=True)

                # Reconstruct the url with the 'page_token' added
                new_url = urlunparse(
                    (
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    )
                )

                new_data, _ = await self.make_api_request(session, url=new_url)
                data_dict.update(new_data.get("bars", {}))

                if data_dict is not None:
                    next_page_token = new_data.get("next_page_token", None)
                else:
                    self.logger.error("Something went wrong with the pagination", stack_info=True)
                    raise RuntimeError("Error while paginating through the data requests.")

            return data_dict



async def gather_data(symbols_batches, api_keys, to_date, cache, session_manager):
    """
    Gathers data for the specified symbols.

    Args:
        symbols_batches (List[List[str]]): The list of batches of stock symbols to gather data for.
        api_keys (str): API keys for authentication.
        to_date (str): The end date for data collection in YYYY-MM-DD format.
        cache (BlacklistSymbolCache): Cache object for storing blacklisted symbols.
        session_manager (HistoricalDataSessionManager): Session manager for handling HTTP sessions.

    Returns:
        List[Dict[str, Any]]: The complete data gathered.
    """
    data_collector = HistoricalDataGathering(
        api_keys, to_date=to_date, cache=cache, session_manager=session_manager
    )
    async with session_manager.manage_session() as session:

        tasks = []
        for batch, _ in symbols_batches:
            # Create a task for each batch of symbol
            tasks.append(asyncio.create_task(
                gather_data_for_batch(batch, session, data_collector)
            ))

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

    initial_data, complete_url = await data_collector.make_api_request(session, symbols=symbols)

    if initial_data.get("next_page_token", None) is not None:
        # If pagination is needed, await the pagination task
        pagination_event.set()

    # Process the initial data
    complete_data = await data_collector.handle_response_pagination(session, initial_data, complete_url)

    return complete_data

def rename_columns(response_data):
    formatted_data = defaultdict(list)
    for batch in response_data:
        for symbol, data in batch.items():
            for i, bar in enumerate(data):
                renamed_bar = {historical_data_mapping[key]: val for key, val in bar.items() if key in historical_data_mapping}
                renamed_bar["symbol"] = symbol
                data[i] = renamed_bar

            formatted_data[symbol] = data

    return formatted_data


def create_dataframes(data_symbols):
    data_list = list(
        itertools.chain.from_iterable(data_symbols.values())
    )
    df = pd.DataFrame(data_list)

    if set(["symbol", "timestamp"]).issubset(df.columns):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index(["symbol", "timestamp"], inplace=True)
    return df


async def check_speed(symbols_iterator, api_keys, cache, session_manager, to_date="2024-05-04"):
    complete_data = await gather_data(symbols_iterator, api_keys, to_date, cache, session_manager)
    with open("output_data.pkl", "wb") as f:
        pickle.dump(complete_data, f)
    return complete_data

async def run_stuff():
    setup_logging()
    api_keys = APIKeys(load_from="config")
    to_date = "2024-05-05"

    cache = BlacklistSymbolCache()
    upcoming_dates = DateRange.get_dates(
        init_offset=1,
        date_window=80,
        init_unit=Unit.DAYS,
        date_window_unit=Unit.DAYS,
    )

    upcoming = UpcomingEarnings(api_keys, cache)
    symbols = upcoming.get_upcoming_earnings_list_strings(
        upcoming_dates.from_date, upcoming_dates.to_date
    )
    symbols_iterator = BatchIteratorWithCount(symbols, fraction=0.025)
    session_manager = HistoricalDataSessionManager(api_keys)

    complete_data = await gather_data(symbols_iterator, api_keys, to_date, cache, session_manager)
    rename_data = rename_columns(complete_data)

    df = create_dataframes(rename_data)
    df.to_parquet('data.parquet')

    table = pq.read_table('data.parquet', use_pandas_metadata=True)
    print(table.schema)
    print(table.slice(0, 5))

if __name__ == "__main__":
    cProfile.run("asyncio.run(run_stuff())", filename="output-async.prof")
