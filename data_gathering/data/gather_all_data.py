import asyncio
import pandas as pd
from tqdm.asyncio import tqdm
from data_gathering.data.upcoming_earnings.get_upcoming_earnings import UpcomingEarnings
from data_gathering.utils import DateUtils
from data_gathering.config.api_keys import APIKeys

from .historical_prices.upcoming_earnings_history import HistoricalData


class DataFetcher:
    def __init__(self):
        self.api_keys = APIKeys.from_config_file()
        self.semaphore = asyncio.Semaphore(12)

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

        # Instantiate classes
        self.historical_data = HistoricalData(
            self.api_keys,
            self.history_dates.from_date,
            self.history_dates.to_date,
            self.semaphore,
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

            self.process_historical_data(self.historical_data.historical_data_by_symbol)
        finally:
            await self.historical_data.finish()

    async def fetch_historical_data(self, symbol, historical_data):
        await historical_data.fetch_historical_data(symbol)

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
    def process_historical_data(self, historical_data_by_symbol):
        # Concatenate all DataFrames into a single DataFrame, aligned on the datetime index
        combined_historical_df = pd.concat(
            historical_data_by_symbol.values(),
            axis=1,
            keys=historical_data_by_symbol.keys(),
        )
        print(combined_historical_df)
