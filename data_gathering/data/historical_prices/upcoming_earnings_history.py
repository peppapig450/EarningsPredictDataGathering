import asyncio
import json

import aiohttp
import pandas as pd
from data_gathering.config.api_keys import APIKeys
from data_gathering.models.mappings import *

class HistoricalData:
    def __init__(
        self,
        api_keys: APIKeys,
        from_date,
        to_date,
        cache,
        data_fetcher,
    ) -> None:
        self.apca_key_id = api_keys.__getattribute__("apca_key_id")
        self.apca_api_secret_key = api_keys.__getattribute__("apca_api_secret_key")
        self.from_date = "1983-01-01"
        self.to_date = to_date
        self.cache = cache
        self.base_url = "https://data.alpaca.markets/v2/stocks/bars"
        self.rest_of_link = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&adjustment=raw&feed=sip&sort=asc"
        self.historical_data_by_symbol = {}
        self.session = None
        self.mapping = historical_data_mapping
        self.data_fetcher = data_fetcher

    def get_headers(self):
        return {
            "accept": "application/json",
            "APCA-API-KEY-ID": self.apca_key_id,
            "APCA-API-SECRET-KEY": self.apca_api_secret_key,
        }

    async def close(self):
        if self.session:
            await self.session.close()

    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.get_headers())
        return self.session

    async def fetch_data(self, symbol):
        url = f"{self.base_url}?symbols={symbol}{self.rest_of_link}"

        session = await self.get_session()
        async with self.data_fetcher.semaphore:
            async with session.get(url) as response:
                data = await response.text
                print(type(data))

                if "bars" not in data or not data["bars"]:
                    # Add symbol to the cache if historical data is empty
                    self.cache.add_symbol(symbol)
                    return None

                try:
                    data = data["bars"]
                    return data
                except KeyError:
                    # Add symbol to the cache if historical data retrieval fails
                    return None

    # TODO: Modify fetch_historical_data to return an Async Generator to use chunks
    # Json normalize taking way too long
    async def fetch_historical_data(self, symbol):
        await asyncio.sleep(0.3)
        data = await self.fetch_data(symbol)
        if data:
            self.historical_data_by_symbol[symbol] = data

    def normalize_and_rename(self, data, symbol):

        df = pd.DataFrame(data)
        # Remap the column names
        normalized_df = normalized_df.rename(columns=self.mapping)

        # Set Datetime column as index
        normalized_df["Datetime"] = pd.to_datetime(normalized_df["Datetime"])
        normalized_df.set_index("Datetime", inplace=True)

        return normalized_df

    async def finish(self):
        if self.session:
            await self.session.close()
        self.cache.save_blacklist_to_pickle()
