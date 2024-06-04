import asyncio
import cProfile
import json
import re
import logging
import pickle
import time
from datetime import date
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

import requests
from aiohttp import ClientSession

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.data.get_upcoming_earnings import UpcomingEarnings
from data_gathering.data.historical.historical_data_session import \
    HistoricalDataSessionManager
from data_gathering.models.date_range import DateRange, Unit
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

    async def async_make_api_request(self, session, symbols=None, url=None):
        if symbols is not None:
            symbols_batch = ",".join(symbols)
            encoded_symbols = quote(symbols_batch)
            base_url: str = "https://data.alpaca.markets/v2/stocks/bars"
            rest_of_url: str = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&asof={date.today().strftime("%Y-%m-%d")}&feed=sip&sort=asc"
            complete_url: str = f"{base_url}?symbols={encoded_symbols}{rest_of_url}"
        elif url is not None:
            complete_url = url
        else:
            raise ValueError("Neither symbols batch nor a url passed")

        try:
            async with session.get(complete_url) as response:
                data = await response.json()
                return data, complete_url
        except Exception as e:
            raise Exception from e

    async def handle_data_pagination(self, session, data, complete_url):
        data_dict = {}
        print(data, flush=True)
        data_dict.update(data["bars"])
        next_page_token = data.get("next_page_token", None)

        while next_page_token:
            self.logger.info("Getting pagination for %s with %s", complete_url, next_page_token)

            parsed_url = urlparse(complete_url) # Parse the url
            query_params = parse_qsl(parsed_url.query) # Split the query parameters

            # Insert the 'next_page_token' before the 'sort' parameter
            for i, (key, value) in enumerate(query_params):
                if key == "sort":
                    query_params.insert(i, ("page_token", next_page_token))
                    break
            else:
                # If 'sort' parameter not found, append the 'page_token' at the end
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
                parsed_url.fragment,
                )
            )

            new_data, _ = await self.async_make_api_request(session, url=new_url)
            data_dict.update(new_data["bars"])
            next_page_token = new_data.get("next_page_token", None)

        return data_dict


    def determine_rerun_request(
        self,
        data,
        complete_url,
    ):

        data_dict = {}
        data_dict.update(data["bars"])
        next_page_token = data.get("next_page_token", None)

        while next_page_token:
            self.logger.info(
                "Getting pagination for %s with %s", complete_url, next_page_token
            )

            parsed_url = urlparse(complete_url)  # Parse the URL
            query_params = parse_qsl(parsed_url.query)  # Split the query parameters

            # Insert the next_page_token before the 'sort' parameter
            for i, (key, value) in enumerate(query_params):
                if key == "sort":
                    query_params.insert(i, ("page_token", next_page_token))
                    break
            else:
                # If 'sort' parameter not found, append the 'page_token' at the end
                query_params.append(("page_token", next_page_token))

            # Encode the new query params
            new_query = urlencode(query_params, doseq=True)

            # Reconstruct the url with the page_token added
            new_url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    new_query,
                    parsed_url.fragment,
                )
            )

            new_data, _ = self.make_api_request(symbols=None, url=new_url)
            data_dict.update(new_data["bars"])
            next_page_token = new_data.get("next_page_token", None)

        return data_dict

    def make_api_request(self, symbols=None, url=None):
        if symbols is not None:
            symbols_batch = ",".join(symbols)
            encoded_symbols = quote(symbols_batch)
            base_url: str = "https://data.alpaca.markets/v2/stocks/bars"
            # TODO: add asof today
            rest_of_url: str = (
                f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&feed=sip&sort=asc"
            )
            complete_url: str = f"{base_url}?symbols={encoded_symbols}{rest_of_url}"
        elif url is not None:
            complete_url = url
        else:
            raise ValueError("Neither symbols batch nor a url passed")

        headers = self.get_headers()

        try:
            response = requests.get(complete_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.logger.info("Gathered data")

            return data, complete_url
        except Exception as e:
            raise Exception from e


async def gather_data(symbols, api_keys, to_date, cache, session_manager):
    data_collector = HistoricalDataGathering(
        api_keys, to_date=to_date, cache=cache, session_manager=session_manager
    )
    async with session_manager.manage_session() as session:
        initial_data, complete_url = await data_collector.async_make_api_request(session, symbols)
        complete_data = await data_collector.handle_data_pagination(session, initial_data, complete_url)

    return complete_data


def get_data(symbols, api_keys, to_date, cache, session):
    data_collector = HistoricalDataGathering(
        api_keys, to_date="2024-05-02", cache=cache, session_manager=session
    )

    data, complete_url = data_collector.make_api_request(symbols)
    complete_data = data_collector.determine_rerun_request(data, complete_url)
    return complete_data

def check_speed(symbols_iterator, api_keys, cache, session_manager, to_date="2024-05-04"):
    data_list = []
    for batch, _ in symbols_iterator:
        #batch_data = asyncio.run(gather_data(batch, api_keys, "2024-05-04", cache, session_manager))
        batch_data = get_data(batch, api_keys, to_date, cache, session_manager)
        data_list.append(batch_data)

if __name__ == "__main__":
    setup_logging()
    api_keys = APIKeys(load_from="config")

    cache = BlacklistSymbolCache()
    upcoming_dates = DateRange.get_dates(
        init_offset=1,
        date_window=14,
        init_unit=Unit.DAYS,
        date_window_unit=Unit.DAYS,
    )

    upcoming = UpcomingEarnings(api_keys, cache)
    symbols = upcoming.get_upcoming_earnings_list_strings(
        upcoming_dates.from_date, upcoming_dates.to_date
    )
    symbols_iterator = BatchIteratorWithCount(symbols, fraction=0.025)
    session_manager = HistoricalDataSessionManager(api_keys)

    cProfile.run("check_speed(symbols_iterator, api_keys, cache, session_manager)", filename="output-noasync.prof")
