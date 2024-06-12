import logging
import re
from typing import Optional

import requests
from pydantic import ValidationError

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.models.exceptions import NoUpcomingEarningsError
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.blacklist_cache import BlacklistSymbolCache
from data_gathering.utils.cache.cache_registry import CacheRegistry


class UpcomingEarnings:
    """
    A class to retrieve upcoming earnings data.

    Attributes:
        api_key (str): The API key for accessing the financial modeling prep API.
        cache_registry (CacheRegistry): The registry to manage cache instances.
        base_url (str): The base URL for the financial modeling prep API.
        logger (logging.Logger): Logger for the class.
        session (requests.Session): A session object to persist certain parameters across requests.

    Methods:
        get_upcoming_earnings_list(from_date: str, to_date: str, timeout: Optional[int] = 20) -> List[UpcomingEarning]:
            Retrieves a list of upcoming earnings within a specified date range.
        get_upcoming_earnings_list_strings(from_date: str, to_date: str, timeout: Optional[int] = 20) -> List[str]:
            Retrieves upcoming earnings symbols as strings within a specified date range.
    """

    def __init__(self, api_keys: APIKeys, cache_registry: CacheRegistry):
        self.api_key = api_keys.get_key(APIService.FMP)
        self.cache_registry = cache_registry
        self.base_url = "https://financialmodelingprep.com/api/v3/earning_calendar"
        self.logger = logging.getLogger(__name__)    

    def get_upcoming_earnings_list(
        self, from_date: str, to_date: str, timeout: Optional[int] = 20
    ) -> list[UpcomingEarning]:
        """
        Retrieves a list of upcoming earnings within a specified date range.

        Args:
            from_date (str): The start date of the date range in the format 'YYYY-MM-DD'.
            to_date (str): The end date of the date range in the format 'YYYY-MM-DD'.
            timeout (int, optional): The request timeout in seconds. Defaults to 20.

        Returns:
            List[UpcomingEarning]: A list of UpcomingEarning objects representing upcoming earnings data.

        Raises:
            NoUpcomingEarningsError: If an error occurs during the retrieval process, or if the parsed data is empty.
                - If the response status code indicates an error (logged).
                - If the response data does not match the expected format (logged).
        """
        @self.cache_registry.cache_decorator(BlacklistSymbolCache)
        def inner_get_upcoming_earnings_list(cache: BlacklistSymbolCache, from_date: str, to_date: str, timeout: Optional[int] = 20) -> list[UpcomingEarning]:
            payload = {"from": from_date, "to": to_date, "apikey": self.api_key}

            response = requests.get(self.base_url, params=payload, timeout=timeout)
            response.raise_for_status()  # Raise for non-2xx status codes
            try:
                response.raise_for_status()
                data = response.json()
                parsed_data = [
                    UpcomingEarning(**item)
                    for item in data
                    if not re.search(r"[-.][A-Z]+$", item["symbol"])
                    and not item["symbol"] in cache
                ]
                if not parsed_data:
                    raise NoUpcomingEarningsError()
                return parsed_data
            except (ValidationError, requests.exceptions.RequestException) as e:
                self.logger.critical(
                    f"Error while retrieving upcoming earnings list: {str(e)}",
                    exc_info=True,
                )
                raise NoUpcomingEarningsError() from e
        
        return inner_get_upcoming_earnings_list(from_date, to_date, timeout)

    def get_upcoming_earnings_list_strings(
        self, from_date: str, to_date: str, timeout=20
    ) -> list[str]:
        """
        Retrieves upcoming earnings symbols as strings within a specified date range.

        This method is a wrapper around `get_upcoming_earnings_list`, providing a convenient way to
        retrieve only the symbols from the upcoming earnings data.

        Args:
            from_date (str): The start date of the date range in the format 'YYYY-MM-DD'.
            to_date (str): The end date of the date range in the format 'YYYY-MM-DD'.
            timeout (int, optional): The request timeout in seconds. Defaults to 20.

        Returns:
            List[str]: A list of symbols for upcoming earnings within the specified date range.

        Raises:
            NoUpcomingEarningsError: If an error occurs during the retrieval process.
        """
        earnings_list = self.get_upcoming_earnings_list(from_date, to_date, timeout)
        return [symbols.symbol for symbols in earnings_list]
