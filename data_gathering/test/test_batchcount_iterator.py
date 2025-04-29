import pytest
from itertools import count
from data_gathering.models import BatchIteratorWithCount


def test_batch_iterator_initialization():
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    fraction = 0.4
    iterator = BatchIteratorWithCount(symbols, fraction)

    assert iterator.batch_size == 2
    assert iterator.total_seen == 0


def test_batch_iterator_batches():
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    fraction = 0.4
    iterator = BatchIteratorWithCount(symbols, fraction)

    batch1, count1 = next(iterator)
    batch2, count2 = next(iterator)
    batch3, count3 = next(iterator)

    assert batch1 == ("AAPL", "GOOGL")
    assert count1 == 1

    assert batch2 == ("MSFT", "AMZN")
    assert count2 == 2

    assert batch3 == ("TSLA",)
    assert count3 == 3


def test_batch_iterator_stop_iteration():
    symbols = ["AAPL", "GOOGL"]
    fraction = 0.5
    iterator = BatchIteratorWithCount(symbols, fraction)

    batch1, count1 = next(iterator)
    batch2, count2 = next(iterator)

    assert batch1 == ("AAPL",)
    assert count1 == 1

    assert batch2 == ("GOOGL",)
    assert count2 == 2

    with pytest.raises(StopIteration):
        next(iterator)


def test_total_seen_property():
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    fraction = 0.4
    iterator = BatchIteratorWithCount(symbols, fraction)

    next(iterator)
    assert iterator.total_seen == 2

    next(iterator)
    assert iterator.total_seen == 4

    next(iterator)
    assert iterator.total_seen == 5
