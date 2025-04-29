import logging
from contextlib import suppress
from csv import DictReader
from csv import Error as CsvError
from datetime import date, datetime
from io import StringIO
from typing import TYPE_CHECKING

import requests

from ..config.api_keys import APIService, ApiKey, APIKeys
from ..exceptions import NoUpcomingEarningsError, UpcomingEarningCreationError
from .upcoming_earning import UpcomingEarning


if TYPE_CHECKING:
    pass
    
class UpcomingEarningsGatherer:
    """
    A class to retrieve upcoming earnings data.

    Attributes:
        api_key (str): The API key for accessing the financial modeling prep API.
        base_url (str): The base URL for the financial modeling prep API.
        logger (logging.Logger): Logger for the class.

    Methods:
        get_upcoming_earnings_list(to_date: str, timeout: Optional[int] = 20) -> List[UpcomingEarning]:
            Retrieves a list of upcoming earnings within a specified date range.
        get_upcoming_earnings_list_strings(to_date: str, timeout: Optional[int] = 20) -> List[str]:
            Retrieves upcoming earnings symbols as strings within a specified date range.
    """
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
        today = datetime.combine(date.today(), datetime.min.time()) 
        
        # Calculate the difference in months
        diff_months = (today - input_date).days // 30
        
        # Target intervals, these are the month values Alpha Vantage's api takes
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
            reader = DictReader(csv_data)

            upcoming_earnings_list: list[UpcomingEarning] = []
            for row in reader:
                # Suppress the error to ignore it, as it's non-critical and is already logged
                with suppress(UpcomingEarningCreationError):
                    upcoming_earnings_list.append(UpcomingEarning.from_dict(row))
                    
            if not upcoming_earnings_list:
                raise NoUpcomingEarningsError("upcoming_earnings_list is empty")
            return upcoming_earnings_list
        
        except CsvError as e:
            message = "CSV parsing error occurred while retrieving upcoming earnings list"
            self.logger.critical(f"{message}: {str(e)}", exc_info=True, stack_info=True)
            raise NoUpcomingEarningsError(message) from e
        
        except requests.exceptions.HTTPError as e:
            message = "HTTP error occurred while retrieving upcoming earnings list"
            self.logger.critical(f"{message}: {str(e)}", exc_info=True, stack_info=True)
            raise NoUpcomingEarningsError(message) from e
        
        except NoUpcomingEarningsError as e:
            message = "No upcoming earnings found"
            self.logger.critical(f"{message}: {str(e)}", exc_info=True, stack_info=True)
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