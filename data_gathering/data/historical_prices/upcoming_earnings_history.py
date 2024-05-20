import asyncio
import aiohttp
import pandas as pd

from data_gathering.config.api_keys import APIKeys


class HistoricalData:
    def __init__(self, api_keys: APIKeys, from_date, to_date) -> None:
        self.apca_key_id = api_keys.__getattribute__("apca_key_id")
        self.apca_api_secret_key = api_keys.__getattribute__("apca_api_secret_key")
        self.session = aiohttp.ClientSession(headers=self.get_headers())
        self.from_date = from_date
        self.to_date = to_date
        self.base_url = "https://data.alpaca.markets/v2/stocks/bars"
        self.rest_of_link = f"&timeframe=1Day&start={self.from_date}&end={self.to_date}&limit=10000&adjustment=raw&feed=sip&sort=asc"
        self.data = pd.DataFrame(
            columns=[
                "Symbol",
                "Close",
                "High",
                "Low",
                "Volume",
                "Open",
                "Datetime",
                "Volume Weighted Average Price",
            ]
        )

    def get_headers(self):
        return {
            "accept": "application/json",
            "APCA-API-KEY-ID": self.apca_key_id,
            "APCA-API-SECRET-KEY": self.apca_api_secret_key,
        }

    async def fetch_data(self, symbol):
        url = f"{self.base_url}?symbols={symbol}{self.rest_of_link}"

        async with self.session.get(url) as response:
            data = await response.json()

            try:
                data = data["bars"]
                return self.normalize_and_rename(data, symbol)
            except KeyError:
                pass

    async def fetch_historical_data(self, symbol):
        data = await self.fetch_data(symbol)
        self.data.append(data)
        return data

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
