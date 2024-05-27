import re

import requests
from pydantic import ValidationError

from data_gathering.config.api_keys import APIKeys
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache


# TODO: Custom types
class UpcomingEarnings:
    def __init__(self, api_keys: APIKeys, cache: BlacklistSymbolCache):
        self.api_key = api_keys.fmp_api_key
        self.cache = cache
        self.base_url = "https://financialmodelingprep.com/api/v3/earning_calendar"

    def get_upcoming_earnngs_list(self, from_date: str, to_date: str, timeout=20):
        payload = {"from": from_date, "to": to_date, "apikey": self.api_key}
        response = requests.get(self.base_url, params=payload, timeout=timeout)
        if response.status_code == 200:
            try:
                data = response.json()
                parsed_data = [
                    UpcomingEarning(**item)
                    for item in data
                    if not re.search(r"[-.][A-Z]+$", item["symbol"])
                    and not self.cache.is_blacklisted(item["symbol"])
                ]
            except ValidationError as e:
                raise e.with_traceback(e.__traceback__)
        else:
            raise requests.exceptions.RequestException.with_traceback(
                requests.exceptions.RequestException.__traceback__
            )

        return parsed_data
