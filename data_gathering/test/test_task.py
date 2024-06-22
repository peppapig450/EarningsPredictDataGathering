import pytest

from data_gathering.models import (
    BatchIteratorWithCount,
    DataCategory,
    RunState,
    Task,
    TaskMeta,
    TaskType,
)

from data_gathering.data.historical.historical_task import HistoricalDataTask


# Define a mock Task class with run_io and run_cpu methods for testing purposes
class MockTask(Task, metaclass=TaskMeta):
    pass


class MockHistoricalDataTask(MockTask):
    def run_io(self):
        return "Gathered historical data"

    def run_cpu(self):
        return "Processed historical data"


@pytest.fixture
def mock_task_meta_historical(mocker):
    """
    Fixture to mock TaskMeta.get_data_category_class.
    """
    mocker.patch.object(
        TaskMeta,
        "get_data_category_class",
        return_value="MockHistoricalDataTask",
    )


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


@pytest.mark.usefixtures("mock_task_meta_historical")
def test_task_initialization(mock_task_meta_historical):
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
    assert isinstance(task, (MockTask, MockHistoricalDataTask))
    assert isinstance(task, MockHistoricalDataTask)
    assert task.symbols == symbols_window

    gathered_historical_data = task.run_io()
    assert gathered_historical_data == "Gathered historical data"

    processed_historical_data = task.run_cpu()
    assert processed_historical_data == "Processed historical data"
