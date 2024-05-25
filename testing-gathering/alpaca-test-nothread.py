import re
import signal
from datetime import datetime
import sys
import math

import fmpsdk
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


class UpcomingSymbols:
    def __init__(self) -> None:
        self.api_key = "1Bo8cqgwItUyx0emLvZOFv2GGX20Bbmm"
        self.symbols = []

    def get_symbols(self):
        earnings_data = fmpsdk.earning_calendar(
            apikey=self.api_key, from_date="2024-05-22", to_date="2024-05-31"
        )
        for earning in earnings_data:
            if (symbol := earning["symbol"]) and (
                not re.search(r"[-.][A-Z]+$", symbol)
            ):
                self.symbols.append(symbol)
        return self.symbols


class Alpaca:
    def __init__(self, api_key, secret_key) -> None:
        self.api_key = api_key
        self.secret_key = secret_key

    def create_client(self) -> StockHistoricalDataClient:
        return StockHistoricalDataClient(self.api_key, self.secret_key)

    def set_request_params(self, symbols, start_date, end_date) -> StockBarsRequest:
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(start_date, str)
            else start_date
        )
        end_date = (
            datetime.strptime(end_date, "%Y-%m-%d")
            if isinstance(end_date, str)
            else end_date
        )
        return StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
        )

    def fetch_data(self, client, request_params):
        data = client.get_stock_bars(request_params)
        return data.df

    def get_historical_data_for_chunk(self, symbols_chunk, start_date, end_date):
        client = self.create_client()
        request_params = self.set_request_params(symbols_chunk, start_date, end_date)
        return self.fetch_data(client, request_params)

    def get_historical_data(self, symbols, start_date, end_date, dataframe=True):
        num_symbols = len(symbols)
        chunk_size = max(math.ceil(num_symbols / 2), 1)
        symbols_chunks = [
            symbols[i : i + chunk_size] for i in range(0, num_symbols, chunk_size)
        ]

        historical_data = []
        for symbols_chunk in symbols_chunks:
            bars = self.get_historical_data_for_chunk(
                symbols_chunk, start_date, end_date
            )
            historical_data.append(bars)

        if dataframe:
            df_list = []
            for chunk_bars in historical_data:
                if isinstance(chunk_bars, str):
                    continue
                else:
                    df_list.append(chunk_bars)
            return pd.concat(df_list)
        return historical_data


if __name__ == "__main__":
    upcoming_symbols = UpcomingSymbols()
    symbol_list = upcoming_symbols.get_symbols()[:10]
    alpaca = Alpaca(
        api_key="AKNO0LZR9NJTASEB6IWZ",
        secret_key="bpvyP8Ci72D2CYGSnW59YachILcLL3lhdtX3emlw",
    )
    data = alpaca.get_historical_data(symbol_list, "1983-01-01", "2024-05-21")
    print(data)
