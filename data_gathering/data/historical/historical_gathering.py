import aiohttp
from data_gathering.config.api_keys import APIKeys, APIService
from collections import defaultdict
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache


class HistoricalDataGathering:
    def __init__(
        self, api_keys: APIKeys, to_date: str, cache: BlacklistSymbolCache
    ) -> None:
        self._apca_key_id, self._apca_api_secret_key = api_keys.get_key(
            APIService.ALPACA
        )

        self.from_date = "1983-01-01"
        self.to_date = to_date
        