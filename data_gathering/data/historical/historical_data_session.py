from typing import Any
from data_gathering.models.async_session_manager import AbstractSessionManager
from data_gathering.config.api_keys import APIKeys, APIService


class HistoricalDataSessionManager(AbstractSessionManager):
    def __init__(self, api_keys: APIKeys):
        self.api_keys = api_keys
        super().__init__()

    def get_base_url(self) -> str:
        return "https://data.alpaca.markets/v2/stocks/bars"

    def get_headers(self) -> dict[str, str]:
        _apca_key_id, _apca_api_secret_key = self.api_keys.get_key(APIService.ALPACA)
        return {
            "APCA-API-KEY-ID": _apca_key_id,
            "APCA-API-SECRET-KEY": _apca_api_secret_key,
        }
