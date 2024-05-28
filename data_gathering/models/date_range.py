# utils.py
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Self
from dataclasses import dataclass


class Unit(str, Enum):
    DAYS = "days"
    WEEKS = "weeks"
    QUARTERS = "quarters"
    MONTHS = "months"
    YEARS = "years"


# TODO: only include valid market days
@dataclass
class DateRange:
    """Represents a range of dates.

    Attributes:
        from_date (str): The start date of the date range in the format 'YYYY-MM-DD'.
        to_date (str): The end date of the date range in the format 'YYYY-MM-DD'.
    """

    from_date: str
    to_date: str

    @classmethod
    def create_from_today(
        cls, init_offset: int, date_window: int, init_unit: Unit, date_window_unit: Unit
    ) -> Self:
        """Creates a DateRange instance starting from today.

        Args:
            init_offset (int): The offset from today's date.
            date_window (int): The size of the date window.
            init_unit (Unit): The unit of the init_offset (days, weeks, or quarters).
            date_window_unit (Unit): The unit of the date_window (days, weeks, or quarters).

        Returns:
            DateRange: A DateRange instance starting from today with the specified offset and window size.
        """
        today = datetime.today()

        init_delta = cls._get_delta(init_offset, init_unit)
        from_date = today + init_delta

        window_delta = cls._get_delta(date_window, date_window_unit)
        to_date = from_date + window_delta

        return cls(
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
        )

    @staticmethod
    def _get_delta(offset: int, unit: Unit) -> timedelta:
        """Calculates the timedelta based on the offset and unit."""
        unit_map = {
            Unit.DAYS: timedelta(days=offset),
            Unit.WEEKS: timedelta(weeks=offset),
            Unit.QUARTERS: timedelta(
                days=offset * 91
            ),  # Approximation for 13 weeks per quarter
            Unit.MONTHS: timedelta(days=offset * 30),
            Unit.YEARS: timedelta(days=offset * 365),
        }
        try:
            return unit_map[unit]
        except KeyError as exc:
            raise ValueError("Invalid Unit provided") from exc

    @classmethod
    def get_dates(
        cls,
        init_offset: Optional[int] = None,
        date_window: Optional[int] = None,
        init_unit: Unit = Unit.DAYS,
        date_window_unit: Unit = Unit.DAYS,
    ) -> Self:
        """Convenience method to get a DateRange instance with default or specified parameters.

        Args:
            init_offset (int, optional): The offset from today's date. Defaults to 1 if not provided.
            date_window (int, optional): The size of the date window. Defaults to 7 if not provided.
            init_unit (Unit, optional): The unit of the init_offset (days, weeks, or quarters). Defaults to Unit.DAYS.
            date_window_unit (Unit, optional): The unit of the date_window (days, weeks, or quarters). Defaults to Unit.DAYS.

        Returns:
            DateRange: A DateRange instance based on the provided or default parameters.
        """
        if init_offset is None:
            init_offset = 0
        if date_window is None:
            date_window = 7

        return cls.create_from_today(
            init_offset, date_window, init_unit, date_window_unit
        )
