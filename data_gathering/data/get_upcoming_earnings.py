import re
from typing import List, Optional

import requests
from pydantic import ValidationError

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache
from data_gathering.models.exceptions import NoUpcomingEarningsError


class UpcomingEarnings:
    """
    Initializes the UpcomingEarnings instance.

    Args:
        api_keys (APIKeys): An instance of APIKeys containing the necessary API key.
        cache (BlacklistSymbolCache): An instance of BlacklistSymbolCache for caching blacklisted symbols.
    """

    def __init__(self, api_keys: APIKeys, cache: BlacklistSymbolCache):
        self.api_key = api_keys.get_key(APIService.FMP)
        self.cache = cache
        self.base_url = "https://financialmodelingprep.com/api/v3/earning_calendar"

    def get_upcoming_earnings_list(
        self, from_date: str, to_date: str, timeout: Optional[int] = 20
    ) -> List[UpcomingEarning]:
        """
        Retrieves a list of upcoming earnings within a specified date range.

        Args:
            from_date (str): The start date of the date range in the format 'YYYY-MM-DD'.
            to_date (str): The end date of the date range in the format 'YYYY-MM-DD'.
            timeout (int, optional): The request timeout in seconds. Defaults to 20.

        Returns:
            List[UpcomingEarning]: A list of UpcomingEarning objects representing upcoming earnings data.

        Raises:
            RuntimeError: If an error occurs during the retrieval process.
                - If the response status code indicates an error.
                - If the response data does not match the expected format.
                - If there are no upcoming earnings data available.
        """
        payload = {"from": from_date, "to": to_date, "apikey": self.api_key}

        with requests.get(self.base_url, params=payload, timeout=timeout) as response:
            response.raise_for_status()  # Raise for non-2xx status codes

            try:
                response.raise_for_status()
                data = response.json()
                parsed_data = [
                    UpcomingEarning(**item)
                    for item in data
                    if not re.search(r"[-.][A-Z]+$", item["symbol"])
                    and not self.cache.is_blacklisted(item["symbol"])
                ]
                if not parsed_data:
                    raise RuntimeError from NoUpcomingEarningsError(
                        "Error while retrieving upcoming earnings list."
                    )
                return parsed_data
            except ValidationError as e:
                raise RuntimeError from e.with_traceback(e.__traceback__)
            except requests.exceptions.RequestException as e:
                raise RuntimeError from e

    def get_upcoming_earnings_list_strings(
        self, from_date: str, to_date: str, timeout=20
    ) -> List[str]:
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
            RuntimeError: If an error occurs during the retrieval process.
        """
        earnings_list = self.get_upcoming_earnings_list(from_date, to_date, timeout)
        return [symbols.symbol for symbols in earnings_list]
