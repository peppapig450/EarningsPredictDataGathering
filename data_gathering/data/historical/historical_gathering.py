import logging
import typing

import aiohttp
from historical_data_session import HistoricalDataSessionManager

from data_gathering.config.api_keys import APIKeys, APIService
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache

type window = tuple[typing.Any, ...]


# initialize class
class HistoricalDataGathering:
    def __init__(
        self,
        api_keys: APIKeys,
        to_date: str,
        cache: BlacklistSymbolCache,
        session_manager: HistoricalDataSessionManager,
    ) -> None:
        self._apca_key_id, self._apca_api_secret_key = api_keys.get_key(
            APIService.ALPACA
        )

        self.from_date: str = "1983-01-01"
        self.to_date: str = to_date
        self.cache: BlacklistSymbolCache = cache
        self.session_manager: HistoricalDataSessionManager = (
            session_manager  # created by task handler
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

    def get_headers(self):
        return {
            "APCA-API-KEY-ID": self._apca_key_id,
            "APCA-API-SECRET-KEY": self._apca_api_secret_key,
        }

    async def collect_historical_data(self, symbols: window):

        if not symbols:
            raise ValueError("Symbols cannot be empty.")

        remaining_base_url: str = "v2/stocks/bars/"
        rest_of_url: str = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}"
        complete_url: str = f"{remaining_base_url}?symbols={symbols}{rest_of_url}"

        async with self.session_manager.manage_session() as session:
            async with session.get(complete_url) as response:
                data_dict = await response.json()
