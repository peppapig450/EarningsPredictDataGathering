import pytest

from data_gathering.models import (
    BatchIteratorWithCount,
    DataCategory,
    RunState,
    Task,
    TaskMeta,
    TaskType,
)


# Define a mock Task class with run_io and run_cpu methods for testing purposes
class MockTask(Task, metaclass=TaskMeta):
    def run_io(self):
        pass

    def run_cpu(self):
        pass


def test_run_state_enum():
    assert RunState.RUN.name == "RUN"
    assert RunState.DONE.name == "DONE"


def test_task_type_enum():
    assert TaskType.IO.name == "IO"
    assert TaskType.CPU.name == "CPU"


def test_data_category_enum():
    categories = [
        DataCategory.HISTORICAL,
        DataCategory.FUNDAMENTALS,
        DataCategory.ANALYST_ESTIMATES,
        DataCategory.MARKET_SENTIMENT,
        DataCategory.INDUSTRY_SECTOR,
        DataCategory.COMPANY_NEWS,
        DataCategory.VOLATILITY,
        DataCategory.EARNINGS_TRANSCRIPTS,
    ]
    assert all(isinstance(category, DataCategory) for category in categories)


def test_data_category_get_next_category():
    assert DataCategory.HISTORICAL.get_next_category == DataCategory.FUNDAMENTALS
    assert (
        DataCategory.EARNINGS_TRANSCRIPTS.get_next_category == DataCategory.HISTORICAL
    )


def test_task_initialization():
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    fraction = 0.4
    iterator = BatchIteratorWithCount(symbols, fraction)

    symbols_window, _ = next(iterator)
    symbols_seen = 1  # Starting with 1 because we've already consumed one batch
    task = MockTask(
        task_type=TaskType.IO,
        data_category=DataCategory.HISTORICAL,
        symbols=symbols_window,
        symbols_seen=symbols_seen,
    )

    assert task.task_type == TaskType.IO
    assert task.data_category == DataCategory.HISTORICAL
    assert task.state == RunState.RUN
    assert task.io_result is None
    assert task.cpu_result is None
    assert task.data_category_class == "HistoricalDataTask"
    assert task.symbols == symbols_window

    # Update symbols_seen and initialize tasks for the next batches
    for batch, count in iterator:
        symbols_seen = count
        task = MockTask(
            task_type=TaskType.IO,
            data_category=DataCategory.HISTORICAL,
            symbols=batch,
            symbols_seen=symbols_seen,
        )


def test_task_meta_missing_methods():
    class IncompleteTask(Task):
        def __init__(self, *, task_type, data_category, symbols, symbols_seen):
            super().__init__(
                task_type=task_type,
                data_category=data_category,
                symbols=symbols,
                symbols_seen=symbols_seen,
            )

    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    fraction = 0.4
    iterator = BatchIteratorWithCount(symbols, fraction)

    symbols_window, _ = next(iterator)
    symbols_seen = 1  # Starting with 1 because we've already consumed one batch

    with pytest.raises(
        TypeError,
        match="Class 'IncompleteTask' must implement 'run_io' and 'run_cpu' methods",
    ):
        task = IncompleteTask(
            task_type=TaskType.IO,
            data_category=DataCategory.HISTORICAL,
            symbols=symbols_window,
            symbols_seen=symbols_seen,
        )
