import asyncio
import aiohttp
import pandas as pd
import json

from data_gathering.config.api_keys import APIKeys


class HistoricalData:
    CACHE_FILE = "symbols_cache.json"

    def __init__(self, api_keys: APIKeys, from_date, to_date, max_sessions=3) -> None:
        self.apca_key_id = api_keys.__getattribute__("apca_key_id")
        self.apca_api_secret_key = api_keys.__getattribute__("apca_api_secret_key")
        self.from_date = from_date
        self.to_date = to_date
        self.semaphore = asyncio.Semaphore(4)
        self.symbols_without_historical_data = self.load_cache_from_file()
        self.base_url = "https://data.alpaca.markets/v2/stocks/bars"
        self.rest_of_link = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&adjustment=raw&feed=sip&sort=asc"
        self.historical_data_by_symbol = {}
        self.session = None

    def load_cache_from_file(self):
        try:
            with open(self.CACHE_FILE, "r") as file:
                return set(json.load(file))
        except FileNotFoundError:
            return set()

    def save_cache_to_file(self):
        existing_cache = self.load_cache_from_file()  # Load existing cache
        updated_cache = existing_cache.union(self.symbols_without_historical_data)
        with open(
            self.CACHE_FILE, "w"
        ) as file:  # Open in "w" mode to overwrite existing contents
            json.dump(list(updated_cache), file)

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
        async with self.semaphore:
            async with session.get(url) as response:
                data = await response.json()

                if "bars" not in data or not data["bars"]:
                    # Add symbol to the cache if historical data is empty
                    self.symbols_without_historical_data.add(symbol)
                    return None

                try:
                    data = data["bars"]
                    return data
                except KeyError:
                    # Add symbol to the cache if historical data retrieval fails
                    return None

    async def fetch_historical_data(self, symbol):
        if symbol in self.symbols_without_historical_data:
            return None

        await asyncio.sleep(0.3)
        data = await self.fetch_data(symbol)
        if data:
            df = self.normalize_and_rename(data, symbol)
            self.historical_data_by_symbol[symbol] = df
            return df

    def normalize_and_rename(self, data, symbol):
        key_mapping = {
            "c": "Close",
            "h": "High",
            "l": "Low",
            "n": "Volume",
            "o": "Open",
            "t": "Datetime",
            "v": "Volume",
            "vw": "Volume Weighted Average Price",
        }

        df = pd.DataFrame(data)
        normalized_df = pd.json_normalize(df[symbol])

        # Remap the column names
        normalized_df = normalized_df.rename(columns=key_mapping)

        # Insert the 'Symbol' column as the first column
        normalized_df.insert(0, "Symbol", symbol)

        # Set Datetime column as index
        normalized_df["Datetime"] = pd.to_datetime(normalized_df["Datetime"])
        normalized_df.set_index("Datetime", inplace=True)

        return normalized_df

    async def finish(self):
        if self.session:
            await self.session.close()
        self.save_cache_to_file()
