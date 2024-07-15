import csv
import io
import logging
import timeit
from dataclasses import InitVar, dataclass
from datetime import date, datetime
from io import StringIO
from pprint import pprint
from typing import Any, NamedTuple
from urllib.parse import urlencode

import pandas as pd
import requests

from data_gathering.config import APIKeys
from data_gathering.config.api_keys import ApiKey, APIService
from data_gathering.exceptions import NoUpcomingEarningsError


# TODO: Symbol can have multiple reportDates and fiscalDates returned when using the 12 month window
# not sure how to handle this with the dataclass or if it's possible.
# Not sure how to create the UpcomingEarning with pandas or to stick with csv reader
# csv reader is faster in benchmarks.
class DateTuple(NamedTuple):
    date: datetime
    date_str: str

    def __str__(self):
        return self.date_str


# XXX: Maybe use InitVar for the initial report_date and fiscal_year_date with kw args or something
# XXX: or subclass DateTuple
@dataclass
class UpcomingEarning:
    symbol: str
    company_name: str
    report_date: str | DateTuple
    fiscal_year_end: str | DateTuple
    currency: str
    date_format: InitVar[str] = "%Y-%m-%d"

    @classmethod
    def from_dict(cls, data: dict[str | Any, str | Any]):
        # Map expected dictionary keys to class attributes
        mapped_data: dict[str, str] = {
            "symbol": data["symbol"],
            "company_name": data["name"],
            "report_date": data["reportDate"],
            "fiscal_year_end": data["fiscalDateEnding"],
            "currency": data["currency"],
        }
        return cls(**mapped_data)

    def _create_date_tuple(self, date_value: str | DateTuple, date_format: str):
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, date_format)
            date_str = date_value
        else:
            date_obj = date_value.date
            date_str = date_value.date_str
        return DateTuple(date_obj, date_str)

    def __post_init__(self, date_format: str):
        self.report_date = self._create_date_tuple(self.report_date, date_format)
        self.fiscal_year_end = self._create_date_tuple(
            self.fiscal_year_end, date_format
        )

    def __str__(self):
        return self.symbol


class UpcomingEarnings:
    def __init__(self, api_keys: APIKeys) -> None:
        self.api_key = api_keys.get_key(APIService.ALPHA_VANTAGE)
        self.base_url = "https://www.alphavantage.co/query"
        self.logger = logging.getLogger(__name__)

    def _calculate_date_proximity(self, target_date: str):
        """
        Calculate the proximity of a given target date to predefined intervals of 3, 6, or 12 months from today.

        Args:
            target_date (str): The target date as a string in the format 'YYYY-MM-DD'.

        Returns:
            int: The interval (3, 6, or 12) months that the difference between today's date and the target date is closest to.

        Raises:
            ValueError: If the target_date is not in the format 'YYYY-MM-DD'.

        Example:
            >>> instance._calculate_date_proximity('2023-01-01')
            6
        """
        input_date = datetime.strptime(target_date, "%Y-%m-%d")
        today = date.today()

        # Calculate the difference in months
        diff_months = (today - input_date).days // 30

        # Target intervals
        intervals = (3, 6, 12)

        # Find the closest interval
        closest = min(intervals, key=lambda month: abs(diff_months - month))

        return closest

    def get_upcoming_earnings_list(
        self, to_date: str, timeout: int = 20
    ) -> list[UpcomingEarning]:
        """
        Retrieve a list of upcoming earnings reports.

        This method calculates the proximity of the given target date to predefined intervals (3, 6, or 12 months)
        and requests the earnings calendar data from an external API. It then parses the CSV response and creates
        a list of `UpcomingEarning` instances.

        Args:
            to_date (str): The target date as a string in the format 'YYYY-MM-DD'.
            timeout (int, optional): The timeout for the API request in seconds. Defaults to 20.

        Returns:
            list[UpcomingEarning]: A list of `UpcomingEarning` instances.

        Raises:
            NoUpcomingEarningsError: If there are no upcoming earnings in the response or if an error occurs during
                                    the retrieval and parsing of the data.

        Example:
            >>> earnings = instance.get_upcoming_earnings_list('2024-08-01')
            >>> for earning in earnings:
            >>>     print(earning)
        """
        month = self._calculate_date_proximity(to_date)
        payload: dict[str, str | ApiKey] = {
            "function": "EARNINGS_CALENDAR",
            "horizon": f"{month}month",
            "apikey": self.api_key,
        }

        response = requests.get(self.base_url, params=payload, timeout=timeout)
        try:
            response.raise_for_status()
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)

            upcoming_earnings_list = [UpcomingEarning.from_dict(row) for row in reader]
            if not upcoming_earnings_list:
                raise NoUpcomingEarningsError
            return upcoming_earnings_list
        except (csv.Error, requests.exceptions.HTTPError, NoUpcomingEarningsError) as e:
            message = "Error while retrieving upcoming earnings list"
            self.logger.critical(f"{message}: {str(e)}", e, exc_info=True, stack_info=True)
            raise NoUpcomingEarningsError(message) from e
    
    def get_upcoming_earnings_list_strings(self, to_date: str, timeout: int = 20) -> list[str]:
        """
        Retrieve a list of upcoming earnings report symbols.

        This method fetches the upcoming earnings reports using the `get_upcoming_earnings_list` method 
        and extracts the symbols of the companies with upcoming earnings.

        Args:
            to_date (str): The target date as a string in the format 'YYYY-MM-DD'.
            timeout (int, optional): The timeout for the API request in seconds. Defaults to 20.

        Returns:
            list[str]: A list of symbols for companies with upcoming earnings reports.

        Raises:
            NoUpcomingEarningsError: If there are no upcoming earnings in the response or if an error occurs 
                                    during the retrieval and parsing of the data.

        Example:
            >>> symbols = instance.get_upcoming_earnings_list_strings('2024-08-01')
            >>> for symbol in symbols:
            >>>     print(symbol)
        """
        earnings_list = self.get_upcoming_earnings_list(to_date, timeout)
        return [earning.symbol for earning in earnings_list]


if __name__ == "__main__":
    api_keys = APIKeys()
    alpha_vantage_key = api_keys.get_key(APIService.ALPHA_VANTAGE)
    url = build_earnings_calendar_url(alpha_vantage_key, 12)

    data = make_api_request_csv(url)
    pprint(data)
    ## Benchmarking using timeit
    # pandas_time = benchmark_csv_parsing(url, "pandas")
    # csv_time = benchmark_csv_parsing(url, "csv")

    # Print results
    # print(f"Average execution time for pandas: {pandas_time:.4f} seconds")
    # print(f"Average execution time for csv: {csv_time:.4f} seconds")
