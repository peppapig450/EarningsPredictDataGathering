import pytest
from data_gathering.models.task_meta import DataCategory, RunState, TaskMeta, TaskType
from data_gathering.models.task import Task


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
    task = MockTask(
        task_id=1,
        task_type=TaskType.IO,
        data_category=DataCategory.HISTORICAL,
        symbols=["AAPL", "GOOGL"],
    )
    assert task.task_id == 1
    assert task.task_type == TaskType.IO
    assert task.data_category == DataCategory.HISTORICAL
    assert task.state == RunState.RUN
    assert task.io_result is None
    assert task.cpu_result is None
    assert task.data_processor_class == "HistoricalDataTask"
    assert task.symbols == ["AAPL", "GOOGL"]


def test_task_meta_missing_methods():
    class IncompleteTask(Task):
        pass

    with pytest.raises(
        TypeError,
        match="Class 'IncompleteTask' must implement 'run_io' and 'run_cpu' methods",
    ):
        task = IncompleteTask(
            task_id=1,
            task_type=TaskType.IO,
            data_category=DataCategory.HISTORICAL,
            symbols=["AAPL", "GOOGL"],
        )
