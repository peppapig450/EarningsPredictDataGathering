import logging
from collections import OrderedDict
from datetime import date
import re
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import aiohttp
from .historical_data_session import HistoricalDataSessionManager

from data_gathering.config.api_keys import APIKeys, APIService

type window = tuple[Any, ...]


# XXX: cache temporarily commented out as its not used.
# TODO: implement caching to properly blacklist symbols with no data
class HistoricalDataGathering:
    def __init__(
        self,
        api_keys: APIKeys,
        from_date: str,
        to_date: str,
        # cache: BlacklistSymbolCache | None = None,
    ) -> None:
        """
        Initializes the HistoricalDataGathering object.

        Args:
            api_keys (APIKeys): API keys for authentication.
            to_date (str): The end date for data collection in YYYY-MM-DD format.
            cache (BlacklistSymbolCache): Cache object for storing blacklisted symbols.
            from_date (str, optional): The start date for data collection in YYYY-MM-DD format. Defaults to "1983-01-01".
        """
        self._apca_key_id, self._apca_api_secret_key = api_keys.get_key(
            APIService.ALPACA
        )

        self.from_date, self.to_date = self._validate_and_init_dates(from_date, to_date)
        # self.cache: BlacklistSymbolCache = cache
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
        compiled_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

        # TODO: custom exception
        if not re.match(compiled_pattern, from_date):
            raise ValueError(
                f"Invalid date string for 'from_date': {from_date}. Use YYYY-MM-DD format."
            )

        if not re.match(compiled_pattern, to_date):
            raise ValueError(
                f"Invalid date string for 'to_date': {to_date}. Use YYYY-MM-DD format."
            )

        return from_date, to_date

    def _build_alpaca_request_url(self, symbols: list[str]) -> str:
        """
        Constructs a request URL for the Alpaca API with the provided stock symbols and
        predefined query parameters.

        Args:
            symbols (List[str]): A list of stock symbols to include in the request.

        Raises:
            ValueError: If no symbols are provided.

        Returns:
            str: The constructed request URL for the Alpaca API.
        """
        # Raise value error if no symbols provided
        if symbols is None or len(symbols) == 0:
            logging.error("No symbols passed to url builder.")
            raise ValueError("No symbols passed to url builder")

        # Base url for our requests, and empty dictionary for query_params
        base_url: str = "https://data.alpaca.markets/v2/stocks/bars"
        query_params: dict[str, str] = {}

        # Set the 'symbols' key to a comma seperated list of symbols
        query_params["symbols"] = ",".join(symbols)

        # Add the other query params to the query_params dict
        query_params |= {
            "timeframe": "1Day",
            "start": self.from_date,
            "end": self.to_date,
            "limit": "10000",
            "asof": date.today().strftime("%Y-%m-%d"),
            "feed": "sip",
            "sort": "asc",
        }

        # Encode the query parameters
        encoded_url = urlencode(query_params)

        # Construct the complete url
        complete_url = f"{base_url}?{encoded_url}"

        return complete_url

    def _build_pagination_url(self, url: str, next_page_token: str) -> str:
        """
        Constructs a pagination URL by appending the provided next_page_token to the given URL.

        Args:
            url (str): The base URL.
            next_page_token (str): The token for the next page of results.

        Returns:
            str: The constructed pagination URL.
        """
        # Parse the url and split the query
        parsed_url = urlparse(url)
        query_params = parse_qsl(parsed_url.query)

        # Add the next page token to the url query parameters
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

        return new_url

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

    # TODO: look into memoization for the urls of the make_api_request and pagination
    # TODO: add symbols that return empty data to blacklist cache
    async def make_api_request(
        self,
        session: aiohttp.ClientSession,
        symbols: window,
        url: Optional[str] = None,
    ) -> tuple[dict[str, Any], str]:
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
            complete_url = self._build_alpaca_request_url(symbols)
        elif url is not None:
            complete_url = url
        else:
            raise ValueError("Neither symbols batch nor a url passed.")

        try:
            async with session.get(complete_url) as response:
                data = await response.json()
                return data, complete_url
        except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError) as err:
            self.logger.error(
                f"Error: {err} - occured while retrieving data from {complete_url}",
                exc_info=True,
            )
            return None  # TODO: raise custom error here instead

    # XXX: refactor this eventually
    async def handle_response_pagination(
        self, session: aiohttp.ClientSession, data, url: str
    ) -> OrderedDict | None:
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

            new_url = self._build_pagination_url(url, next_page_token)

            new_data, _ = await self.make_api_request(session, url=new_url)
            data_dict.update(new_data.get("bars", {}))

            if data_dict is not None:
                next_page_token = new_data.get("next_page_token", None)
            else:
                self.logger.error(
                    "Something went wrong with the pagination", stack_info=True
                )
                raise RuntimeError("Error while paginating through the data requests.")

        return data_dict
