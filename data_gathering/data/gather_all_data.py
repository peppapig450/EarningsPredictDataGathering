import asyncio
import json
import pandas as pd
from tqdm.asyncio import tqdm
from data_gathering.data.upcoming_earnings.get_upcoming_earnings import UpcomingEarnings
from data_gathering.utils import DateUtils
from data_gathering.config.api_keys import APIKeys

from .historical_prices.upcoming_earnings_history import HistoricalData
from data_gathering.utils.output_utils.historical_data.historical_data_output_utils import (
    HistoricalDataOutputUtils,
)


class DataFetcher:
    def __init__(self):
        self.api_keys = APIKeys.from_config_file()
        self.semaphore = asyncio.Semaphore(4)

        # Initialize date ranges
        self.history_dates = DateUtils.get_dates(
            init_offset=-4,
            date_window=3,
            init_unit="quarters",
            date_window_unit="quarters",
        )
        self.upcoming_dates = DateUtils.get_dates(
            init_offset=3, date_window=5, date_window_unit="days", init_unit="days"
        )

        # TODO: later add config option for this
        self.historical_symbols_json = {}
        self.hist_json = True

        # Instantiate classes
        self.historical_data = HistoricalData(
            self.api_keys,
            self.history_dates.from_date,
            self.history_dates.to_date,
            self,
        )
        self.upcoming_earnings = UpcomingEarnings(self.api_keys)
        # self.logger = get_logger(__name__)

    async def fetch_all_data(self):

        async def fetch_with_semaphore(symbol, func, **kwargs):
            async with self.semaphore:
                await func(symbol, **kwargs)

        try:
            # Get upcoming earnings with generator
            async for upcoming_earning in tqdm(
                self.upcoming_earnings.get_upcoming_earnings(
                    self.upcoming_dates.from_date, self.upcoming_dates.to_date
                ),
                desc="Fetching data",
                unit=" symbols",
                leave=False,
            ):
                symbol = str(upcoming_earning.symbol)
                if symbol in self.historical_data.symbols_without_historical_data:
                    continue

                # Fetch all types of data for the symbol concurrently
                await asyncio.gather(
                    fetch_with_semaphore(
                        symbol,
                        self.fetch_historical_data,
                        historical_data=self.historical_data,
                    ),
                    fetch_with_semaphore(symbol, self.fetch_fundamental_metrics),
                    fetch_with_semaphore(symbol, self.fetch_analyst_estimates),
                    fetch_with_semaphore(
                        symbol, self.fetch_market_sentiment_indicators
                    ),
                    fetch_with_semaphore(symbol, self.fetch_industry_sector_data),
                    fetch_with_semaphore(symbol, self.fetch_company_news_events),
                    fetch_with_semaphore(symbol, self.fetch_volatility_trading_volume),
                    fetch_with_semaphore(symbol, self.fetch_earnings_call_transcripts),
                )

                await self.process_historical_data()

        finally:

            await self.historical_data.finish()
            # if self.hist_json:
            #    await self.write_json_files()

    async def fetch_historical_data(self, symbol, historical_data):
        await historical_data.fetch_historical_data(symbol)
        # await self.process_historical_data(symbol, symbol_historical_data)

    async def fetch_fundamental_metrics(self, symbol):
        # Fetch fundamental metrics data and process it
        pass

    async def fetch_analyst_estimates(self, symbol):
        # Fetch analyst estimates data and process it
        pass

    async def fetch_market_sentiment_indicators(self, symbol):
        # Fetch market sentiment indicators data and process it
        pass

    async def fetch_industry_sector_data(self, symbol):
        # Fetch industry and sector data for the symbol and process it
        pass

    async def fetch_company_news_events(self, symbol):
        # Fetch company news and events data for the symbol and process it
        pass

    async def fetch_volatility_trading_volume(self, symbol):
        # Fetch volatility and trading volume data for the symbol and process it
        pass

    async def fetch_earnings_call_transcripts(self, symbol):
        # Fetch earnings call transcripts for the symbol and process them
        pass

    # Define a function to process historical data
    async def process_historical_data(self):
        # Concatenate all DataFrames into a single DataFrame, with a multiindex of Datetime and Symbol
        combined_historical_df = HistoricalDataOutputUtils.combine_symbol_dataframes(
            self.historical_data.historical_data_by_symbol
        )
        combined_historical_df.to_pickle("output/output_dataframe.pkl")

        # combined_historical_df.to_parquet(
        #    "output/historical_data.parquet", compression="zstd", engine="pyarrow"
        # )

    async def write_json_files(self):
        # Serialize all JSON data
        all_json_data = json.dumps(self.historical_symbols_json)

        # Iterate over symbol JSON data and write to files
        output_file = "output/output_symbols.json"
        with open(output_file, "w") as file:
            file.write(all_json_data)

    # async def process_and_stream_json
