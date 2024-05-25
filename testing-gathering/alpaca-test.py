import asyncio
import cProfile
import math
import multiprocessing
import pstats
import re
import signal
import sys
from datetime import datetime

import fmpsdk
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


class EmptyDataException(Exception):
    pass


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

    async def fetch_data_async(self, client, request_params):
        result = await asyncio.to_thread(client.get_stock_bars, request_params)
        if result.df.empty:
            raise EmptyDataException("DataFrame is empty")
        return result.df

    async def get_historical_data_for_chunk(self, symbols_chunk, start_date, end_date):
        client = self.create_client()
        request_params = self.set_request_params(symbols_chunk, start_date, end_date)
        try:
            return await self.fetch_data_async(client, request_params)
        except EmptyDataException:
            return None

    def get_historical_data_for_chunk_sync(self, symbols_chunk, start_date, end_date):
        return asyncio.run(
            self.get_historical_data_for_chunk(symbols_chunk, start_date, end_date)
        )

    def get_historical_data(self, symbols, start_date, end_date, dataframe=True):
        num_cores = max(multiprocessing.cpu_count() // 2, 1)
        total_symbols = len(symbols)
        max_tasks_per_child = 2
        chunk_size = max(
            math.ceil(total_symbols / (num_cores * max_tasks_per_child)), 1
        )
        print(f"Number of processes: {num_cores}")
        print(f"Total symbols: {total_symbols}")
        print(f"Chunk size: {chunk_size}")
        print(f"Number of chunks: {math.ceil(total_symbols / chunk_size)}")

        symbols_chunks = [
            symbols[i : i + chunk_size] for i in range(0, total_symbols, chunk_size)
        ]

        def signal_handler(sig, frame):
            print("\nReceived KeyboardInterupt. Terminating..")
            sys.exit(1)

        original_sigint_handler = signal.signal(signal.SIGINT, signal_handler)

        with multiprocessing.Pool(
            processes=num_cores, maxtasksperchild=max_tasks_per_child
        ) as pool:
            tasks = [
                pool.apply_async(
                    self.get_historical_data_for_chunk_sync,
                    args=(symbols_chunk, start_date, end_date),
                )
                for symbols_chunk in symbols_chunks
            ]
            results = [task.get() for task in tasks]

        signal.signal(signal.SIGINT, original_sigint_handler)

        if dataframe:
            df_list = []
            for chunk_bars in results:
                if chunk_bars is not None:
                    df_list.append(chunk_bars)
            return pd.concat(df_list)
        return results


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    upcoming_symbols = UpcomingSymbols()
    symbol_list = upcoming_symbols.get_symbols()
    alpaca = Alpaca(
        api_key="AKNO0LZR9NJTASEB6IWZ",
        secret_key="bpvyP8Ci72D2CYGSnW59YachILcLL3lhdtX3emlw",
    )
    data = alpaca.get_historical_data(symbol_list, "1983-01-01", "2024-05-21")
    print(data.info(verbose=True))
    data.to_parquet("output.parquet", compression="zstd", engine="pyarrow")
    profiler.disable()
    profiler.dump_stats("profile_full2.prof")
