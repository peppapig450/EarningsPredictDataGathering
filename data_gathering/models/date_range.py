# utils.py
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Optional, Self
from dataclasses import dataclass


class TimeUnit(StrEnum):
    DAYS = "days"
    WEEKS = "weeks"
    QUARTERS = "quarters"
    MONTHS = "months"
    YEARS = "years"

    def __new__(cls, value):
        # Create a new instance of the enum
        time_unit = str.__new__(cls, value)
        # Store the value in lowercase to ensure case insensitivity
        time_unit._value_ = value.lower()
        return time_unit

    @classmethod
    def _missing_(cls, value) -> Any:
        # Look for a matching enum member in a case-insensitive way
        for member in cls:
            if member.value == str(value).lower():
                return member
        # If no match is found, call the superclass method
        return super()._missing_(value)


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
        cls,
        init_offset: int,
        date_window: int,
        init_unit: TimeUnit,
        date_window_unit: TimeUnit,
    ) -> Self:
        """Creates a DateRange instance starting from today.

        Args:
            init_offset (int): The offset from today's date.
            date_window (int): The size of the date window.
            init_unit (TimeUnit): The unit of the init_offset (days, weeks, or quarters).
            date_window_unit (TimeUnit): The unit of the date_window (days, weeks, or quarters).

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
    def _get_delta(offset: int, unit: TimeUnit) -> timedelta:
        """Calculates the timedelta based on the offset and unit."""
        # Mixin with timeunit enum?
        unit_map = {
            TimeUnit.DAYS: timedelta(days=offset),
            TimeUnit.WEEKS: timedelta(weeks=offset),
            TimeUnit.QUARTERS: timedelta(
                days=offset * 91
            ),  # Approximation for 13 weeks per quarter
            TimeUnit.MONTHS: timedelta(days=offset * 30),
            TimeUnit.YEARS: timedelta(days=offset * 365),
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
        init_unit: TimeUnit = TimeUnit.DAYS,
        date_window_unit: TimeUnit = TimeUnit.DAYS,
    ) -> Self:
        """Convenience method to get a DateRange instance with default or specified parameters.

        Args:
            init_offset (int, optional): The offset from today's date. Defaults to 1 if not provided.
            date_window (int, optional): The size of the date window. Defaults to 7 if not provided.
            init_unit (TimeUnit, optional): The unit of the init_offset (days, weeks, or quarters). Defaults to TimeUnit.DAYS.
            date_window_unit (TimeUnit, optional): The unit of the date_window (days, weeks, or quarters). Defaults to TimeUnit.DAYS.

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
