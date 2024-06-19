import logging
from collections import OrderedDict
from datetime import date
from re import compile as rcompile
from typing import Any, Optional
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

import aiohttp
from .historical_data_session import HistoricalDataSessionManager

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache

type window = tuple[Any, ...]


class HistoricalDataGathering:
    def __init__(
        self,
        api_keys: APIKeys,
        to_date: str,
        cache: BlacklistSymbolCache,
        session_manager: HistoricalDataSessionManager,
        from_date: str = "1983-01-01",
    ) -> None:
        """
        Initializes the HistoricalDataGathering object.

        Args:
            api_keys (APIKeys): API keys for authentication.
            to_date (str): The end date for data collection in YYYY-MM-DD format.
            cache (BlacklistSymbolCache): Cache object for storing blacklisted symbols.
            session_manager (HistoricalDataSessionManager): Session manager for handling HTTP sessions.
            from_date (str, optional): The start date for data collection in YYYY-MM-DD format. Defaults to "1983-01-01".
        """
        self._apca_key_id, self._apca_api_secret_key = api_keys.get_key(
            APIService.ALPACA
        )

        self.from_date, self.to_date = self._validate_and_init_dates(from_date, to_date)
        self.cache: BlacklistSymbolCache = cache
        self.session_manager: HistoricalDataSessionManager = (
            session_manager  # created by task handler
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

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
        compiled_pattern = rcompile(
            r"^\d{4}\-(0?[1-9]/1[0-2])\-(0?[1-9]/[12][0-9]/3[01])$"
        )

        if not compiled_pattern.match(from_date):
            raise ValueError(
                f"Invalid date string for 'from_date': {from_date}. Use YYYY-MM-DD format."
            )

        if not compiled_pattern.match(to_date):
            raise ValueError(
                f"Invalid date string for 'to_date': {to_date}. Use YYYY-MM-DD format."
            )

        return from_date, to_date

    def get_headers(self) -> dict[str, str]:
        """
        Generates the headers for API requests.

        Returns:
            Dict[str, str]: A dictionary containing the API headers.
        """
        return {
            "APCA-API-KEY-ID": self._apca_key_id,
            "APCA-API-SECRET-KEY": self._apca_api_secret_key,
        }

    # TODO: figure how to use callable to annotate session
    # TODO: add symbols that return empty data to blacklist cache
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
                return data, response.url
        except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError) as err:
            self.logger.error(f"Error: {err} - occured while retrieving data from {complete_url}", exc_info=True)
            return None #TODO: raise custom error here instead


    #XXX: refactor this eventually
    async def handle_response_pagination(self, session, data, url: str) -> OrderedDict | None:
        """
        Handles the pagination for API responses.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to be used for the requests.
            data (Dict[str, Any]): The initial response data.
            url (str): The complete URL for the request.

        Returns:
            OrderedDict: The complete data gathered from all pages.
        """
        if not data and not url:
            return None

        data_dict = OrderedDict()
        data_dict.update(data.get("bars", None))
        next_page_token = data.get("next_page_token", None)


        while next_page_token:
            self.logger.debug(f"Getting pagination for {url} with {next_page_token}")

            # Parse the url
            parsed_url = urlparse(url)
            query_params = parse_qsl(parsed_url.query) # split the query

            # Insert the 'next_page_token' before the 'sort parameter
            for i, (key, _) in enumerate(query_params):
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
