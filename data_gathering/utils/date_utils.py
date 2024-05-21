# utils.py
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Optional, Union

from dateutil.relativedelta import relativedelta


class DateUtils:
    @staticmethod
    def get_dates(
        init_offset: Optional[Union[int, None]] = None,
        date_window: Optional[Union[int, None]] = None,
        init_unit: str = "days",
        date_window_unit: str = "days",
    ) -> namedtuple:
        """
        Calculates dates for earnings data retrieval based on user input.

        Args:
            init_offset (int, optional): The desired offset from today.
                                        A positive value adds, negative subtracts.
                                        Defaults to None.
            date_window (int, optional): The desired window size between 'from_date' and 'to_date'.
                                        Defaults to None (same unit as init_offset).
            init_unit (str, optional): Unit for 'init_offset' (either "days", "weeks", "or "quarters").
                                        Defaults to "days".
            date_window_unit (str, optional): Unit for 'date_window' (either "days", "weeks", or "quarters").
                                                Defaults to "days" (same unit as init_offset).

        Returns:
            DateRange: A named tuple containing 'from_date' and 'to_date' in YYYY-MM-DD format.

        Raises:
            ValueError: If 'init_unit' or 'date_window_unit' are not "days", "weeks", or "quarters
        """
        DateRange = namedtuple("DateRange", ["from_date", "to_date"])

        # ensure input validity
        valid_units = ("days", "weeks", "quarters")
        if init_unit not in valid_units or date_window_unit not in valid_units:
            raise ValueError(
                "init_unit and date_window_unit must be either 'days', 'weeks', or 'quarters'"
            )

        today = datetime.today()

        # TODO: fix the months and years
        if init_offset is not None:
            if init_unit == "days":
                offset_delta = timedelta(days=init_offset)
            elif init_unit == "weeks":
                offset_delta = timedelta(weeks=init_offset)
            elif init_unit == "quarters":
                offset_delta = relativedelta(months=init_offset * 3)
            elif init_unit == "months":
                offset_delta = relativedelta(months=init_offset)
            elif init_unit == "years":
                offset_delta = relativedelta(years=init_offset)

            from_date_dt = today + offset_delta
            from_date = from_date_dt.strftime("%Y-%m-%d")

            if date_window is not None:
                if date_window_unit == "days":
                    window_delta = timedelta(days=date_window)
                elif date_window_unit == "weeks":
                    window_delta = timedelta(weeks=date_window)
                elif date_window_unit == "quarters":
                    window_delta = relativedelta(months=date_window * 3)
                elif date_window_unit == "months":
                    window_delta = relativedelta(month=init_offset)
                elif date_window_unit == "years":
                    window_delta = relativedelta(years=init_offset)

            to_date_dt = from_date_dt + window_delta
            to_date = to_date_dt.strftime("%Y-%m-%d")

        return DateRange(from_date, to_date)
