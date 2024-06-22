import pytest

from data_gathering.models import (
    BatchIteratorWithCount,
    DataCategory,
    RunState,
    Task,
    TaskType,
)

from data_gathering.data.historical.historical_task import HistoricalDataTask


# Define a mock Task class with run_io and run_cpu methods for testing purposes


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
