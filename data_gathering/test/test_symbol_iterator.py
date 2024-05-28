import pytest
from itertools import islice
from datetime import date

from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.models.symbol_iterator import UpcomingEarningsIterator


def test_iterator():
    earnings = [
        UpcomingEarning(symbol="AAPL", date=date(2024, 6, 1)),
        UpcomingEarning(symbol="GOOG", date=date(2024, 6, 2)),
        UpcomingEarning(symbol="MSFT", date=date(2024, 6, 3)),
    ]
    iterator = UpcomingEarningsIterator(earnings)

    # Test __iter__ and __next__
    symbols = list(iterator)
    assert symbols == ["AAPL", "GOOG", "MSFT"]

    # Reset iterator
    iterator = UpcomingEarningsIterator(earnings)
    iter(iterator)
    assert next(iterator) == "AAPL"
    assert next(iterator) == "GOOG"
    assert next(iterator) == "MSFT"
    with pytest.raises(StopIteration):
        next(iterator)


def test_cyclic_iterator():
    earnings = [
        UpcomingEarning(symbol="AAPL", date=date(2024, 6, 1)),
        UpcomingEarning(symbol="GOOG", date=date(2024, 6, 2)),
        UpcomingEarning(symbol="MSFT", date=date(2024, 6, 3)),
    ]
    iterator = UpcomingEarningsIterator(earnings)
    cyclic_iter = iterator.cyclic_iterator()

    # Test cyclic_iterator
    cyclic_symbols = list(islice(cyclic_iter, 6))
    assert cyclic_symbols == ["AAPL", "GOOG", "MSFT", "AAPL", "GOOG", "MSFT"]


def test_windows_iterator():
    # Define test data
    earnings = [
        UpcomingEarning(symbol="AAPL", date=date(2024, 6, 1)),
        UpcomingEarning(symbol="GOOG", date=date(2024, 6, 2)),
        UpcomingEarning(symbol="MSFT", date=date(2024, 6, 3)),
        UpcomingEarning(symbol="AMZN", date=date(2024, 6, 4)),
        UpcomingEarning(symbol="FB", date=date(2024, 6, 5)),
    ]
    iterator = UpcomingEarningsIterator(earnings)

    # Test window_iterator with fraction=0.4
    window_iter = iterator.window_iterator(fraction=0.4)
    windows = list(window_iter)
    expected_windows = [
        ("AAPL", "GOOG"),
        ("MSFT", "AMZN"),
        ("FB", None),
    ]
    assert windows == expected_windows

    # Test window_iterator with fraction=0.6
    window_iter = iterator.window_iterator(fraction=0.6)
    windows = list(window_iter)
    expected_windows = [("AAPL", "GOOG", "MSFT"), ("AMZN", "FB", None)]
    assert windows == expected_windows
