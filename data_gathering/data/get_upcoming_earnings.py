import re
from typing import List

import requests
from pydantic import ValidationError

from data_gathering.config.api_keys import APIKeys
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache


class NoUpcomingEarningsError(Exception):
    pass


class UpcomingEarnings:
    def __init__(self, api_keys: APIKeys, cache: BlacklistSymbolCache):
        self.api_key = api_keys.fmp_api_key
        self.cache = cache
        self.base_url = "https://financialmodelingprep.com/api/v3/earning_calendar"

    def get_upcoming_earnings_list(
        self, from_date: str, to_date: str, timeout=20
    ) -> List[UpcomingEarning]:
        payload = {"from": from_date, "to": to_date, "apikey": self.api_key}
        response = requests.get(self.base_url, params=payload, timeout=timeout)
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
        earnings_list = self.get_upcoming_earnings_list(from_date, to_date, timeout)
        return [symbols.symbol for symbols in earnings_list]
