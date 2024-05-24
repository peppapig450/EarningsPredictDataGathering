import asyncio

import fmpsdk

from data_gathering.config.api_keys import APIKeys
from data_gathering.models.symbols import Symbol
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache


class UpcomingEarnings:
    def __init__(self, api_keys: APIKeys, cache: BlacklistSymbolCache):
        self.api_key = api_keys.fmp_api_key
        self.blacklist = cache.blacklist

    async def get_upcoming_earnings(self, from_date, to_date):
        async def upcoming_earnings_generator():
            upcoming_earnings_list = await asyncio.to_thread(
                fmpsdk.earning_calendar,
                apikey=self.api_key,
                from_date=from_date,
                to_date=to_date,
            )

            for earning in upcoming_earnings_list:
                if symbol := earning.get("symbol"):
                    if not symbol in self.blacklist:
                        symbol = Symbol.create(symbol)
                        if symbol and (earnings_date := earning.get("date")):
                            yield UpcomingEarning(symbol, earnings_date)

        async for earnings in upcoming_earnings_generator():
            yield earnings
