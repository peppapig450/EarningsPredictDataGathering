import pytest
from data_gathering.utils import DateUtils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def test_get_dates_default():
    result = DateUtils.get_dates()
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date


def test_get_dates_specific_values():
    result = DateUtils.get_dates(
        init_offset=5, date_window=10, init_unit="days", date_window_unit="days"
    )
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date
    from_date_dt = datetime.strptime(result.from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(result.to_date, "%Y-%m-%d")
    assert (to_date_dt - from_date_dt).days == 10


def test_get_dates_different_units_weeks():
    result = DateUtils.get_dates(
        init_offset=2, date_window=1, init_unit="weeks", date_window_unit="weeks"
    )
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date
    from_date_dt = datetime.strptime(result.from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(result.to_date, "%Y-%m-%d")
    assert (to_date_dt - from_date_dt).days == 7


def test_get_dates_different_units_quarters():
    result = DateUtils.get_dates(
        init_offset=3, date_window=2, init_unit="quarters", date_window_unit="quarters"
    )
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date
    from_date_dt = datetime.strptime(result.from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(result.to_date, "%Y-%m-%d")
    assert (to_date_dt.year - from_date_dt.year) * 12 + (
        to_date_dt.month - from_date_dt.month
    ) == 6


def test_get_dates_invalid_units():
    with pytest.raises(ValueError):
        DateUtils.get_dates(
            init_offset=2,
            date_window=1,
            init_unit="invalid",
            date_window_unit="invalid",
        )

    with pytest.raises(ValueError):
        DateUtils.get_dates(
            init_offset=2, date_window=1, init_unit="days", date_window_unit="invalid"
        )


def test_get_dates_negative_values():
    result = DateUtils.get_dates(
        init_offset=-5, date_window=10, init_unit="days", date_window_unit="days"
    )
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date
    from_date_dt = datetime.strptime(result.from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(result.to_date, "%Y-%m-%d")
    assert (to_date_dt - from_date_dt).days == 10


def test_get_dates_none_values():
    result = DateUtils.get_dates(init_offset=None, date_window=None)
    assert isinstance(result, tuple)
    assert hasattr(result, "from_date")
    assert hasattr(result, "to_date")
    assert result.from_date < result.to_date
