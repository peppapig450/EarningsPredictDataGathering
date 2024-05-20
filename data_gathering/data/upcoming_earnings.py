import fmpsdk
from data_gathering.models.symbols import Symbol
from data_gathering.config.api_keys import APIKeys


class UpcomingEarnings:
    def __init__(self):
        api_keys = APIKeys.from_config_file()
        self.api_key = api_keys.fmp_api_key

    def get_upcoming_earnings(self, from_date, to_date):
        def upcoming_earnings_generator():
            upcoming_earnings_list = fmpsdk.earning_calendar(
                apikey=self.api_key, from_date=from_date, to_date=to_date
            )
            for earning in upcoming_earnings_list:
                if symbol := earning.get("symbol"):
                    yield Symbol.create(symbol)

        return upcoming_earnings_generator()
