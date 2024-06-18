import pytest
from datetime import datetime, timedelta
from data_gathering.models.date_range import DateRange, TimeUnit


def test_create_from_today():
    # Create a DateRange instance from default parameters
    date_range_default = DateRange.create_from_today(0, 7, TimeUnit.DAYS, TimeUnit.DAYS)

    # check if the from_date is today's date
    assert date_range_default.from_date == datetime.today().strftime("%Y-%m-%d")

    # Create a DateRange instance with custom parameters
    date_range_custom = DateRange.create_from_today(
        2, 14, TimeUnit.WEEKS, TimeUnit.WEEKS
    )

    # Check if the from_date is 2 weeks ahead of today's date
    from_date_custom = datetime.today() + timedelta(weeks=2)
    assert date_range_custom.from_date == from_date_custom.strftime("%Y-%m-%d")

    # Check if the to_date is 14 weeks ahead of from_date
    to_date_custom = from_date_custom + timedelta(weeks=14)
    assert date_range_custom.to_date == to_date_custom.strftime("%Y-%m-%d")

    # Create a DateRange instance with negative offset
    date_range_negative = DateRange.create_from_today(
        -7, 14, TimeUnit.DAYS, TimeUnit.DAYS
    )

    # Check if the from date is 7 days before today's date
    from_date_negative = datetime.today() - timedelta(days=7)
    assert date_range_negative.from_date == from_date_negative.strftime("%Y-%m-%d")

    # Check if the to_date is 14 days ahead of from_date
    to_date_negative = from_date_negative + timedelta(days=14)
    assert date_range_negative.to_date == to_date_negative.strftime("%Y-%m-%d")


def test_get_dates():
    # Get a DateRange instance with default parameters
    date_range_default = DateRange.get_dates()

    # Check if the from_date is today's date
    assert date_range_default.from_date == datetime.today().strftime("%Y-%m-%d")

    # Check if the to_date is 7 days ahead
    assert date_range_default.to_date == (
        datetime.today() + timedelta(days=7)
    ).strftime("%Y-%m-%d")

    # Get a DateRange instance with custom parameters
    date_range_custom = DateRange.get_dates(
        init_offset=3,
        date_window=21,
        init_unit=TimeUnit.MONTHS,
        date_window_unit=TimeUnit.DAYS,
    )

    # Check if the from_date is 3 months ahead of today's date
    from_date_custom = datetime.today() + timedelta(
        days=3 * 30
    )  # Approximation for 3 months
    assert date_range_custom.from_date == from_date_custom.strftime("%Y-%m-%d")

    # Check if the to_date is 21 days ahead of from_date
    to_date_custom = from_date_custom + timedelta(days=21)
    assert date_range_custom.to_date == to_date_custom.strftime("%Y-%m-%d")

    # Get a DateRange instance witht a negative offset
    date_range_negative = DateRange.get_dates(
        init_offset=-1,
        date_window=-7,
        init_unit=TimeUnit.WEEKS,
        date_window_unit=TimeUnit.DAYS,
    )

    # Check if the from_date is 1 week before today's date
    from_date_negative = datetime.today() - timedelta(weeks=1)
    assert date_range_negative.from_date == from_date_negative.strftime("%Y-%m-%d")

    # Check if the to_date is 7 days before from_date
    to_date_negative = from_date_negative - timedelta(days=7)
    assert date_range_negative.to_date == to_date_negative.strftime("%Y-%m-%d")
