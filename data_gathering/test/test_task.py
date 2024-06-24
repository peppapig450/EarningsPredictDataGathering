import importlib
from unittest.mock import MagicMock, patch

import pytest

from data_gathering.data.historical.historical_task import HistoricalDataTask
from data_gathering.models import (
    DataCategory,
    RunState,
    TaskCreationError,
    TaskCreator,
    TaskType,
)
from data_gathering.config import Config, APIKeys


@pytest.fixture
def config():
    api_keys = MagicMock(spec=APIKeys)
    return Config(api_keys=api_keys)


@pytest.fixture
def task_creator(config):
    return TaskCreator(config)


def test_create_task_historical(task_creator):
    task_type = MagicMock(spec=TaskType)
    data_category = DataCategory.HISTORICAL
    symbols = ((1, 2, 3), 4)
    symbols_seen = 5

    with patch.object(
        TaskCreator, "_get_class_from_category", return_value=HistoricalDataTask
    ):
        task = task_creator.create_task(task_type, data_category, symbols, symbols_seen)
        assert isinstance(task, HistoricalDataTask)
        assert task.task_type == task_type
        assert task.data_category == data_category
        assert task.symbols == symbols
        assert task.symbols_seen == symbols_seen
        assert task.api_keys == task_creator.api_keys


def test_create_task_invalid_category(task_creator):
    task_type = MagicMock(spec=TaskType)
    data_category = MagicMock()
    symbols = ((1, 2, 3), 4)
    symbols_seen = 5

    with pytest.raises(
        TaskCreationError, match="Something went wrong creating the class"
    ):
        task_creator.create_task(task_type, data_category, symbols, symbols_seen)


def test_get_class_from_category(task_creator):
    data_category = DataCategory.HISTORICAL

    with patch.object(
        task_creator,
        "_get_module_path_from_category",
        return_value="data_gathering.data.historical.historical_task",
    ):
        with patch(
            "importlib.import_module",
            return_value=MagicMock(Historical=HistoricalDataTask),
        ):
            _class = task_creator._get_class_from_category(data_category)
            assert _class.name == "mock.HistoricalDataTask"


def test_get_module_path_from_category(task_creator):
    data_category = MagicMock()
    data_category.get_task_class_path = MagicMock(
        return_value="data_gathering.data.historical.historical_task"
    )

    module_path = task_creator._get_module_path_from_category(data_category)
    assert module_path == "data_gathering.data.historical.historical_task"


def test_get_module_path_from_category_failure(task_creator):
    data_category = MagicMock()
    data_category.get_task_class_path = MagicMock(return_value=None)

    with pytest.raises(
        TaskCreationError, match="Something went wrong retrieving the module path from"
    ):
        task_creator._get_module_path_from_category(data_category)


def test_get_class_object(task_creator):
    module_path = "data_gathering.data.historical.historical_task"

    with patch(
        "importlib.import_module", return_value=MagicMock(Historical=HistoricalDataTask)
    ):
        _class = task_creator._get_class_object(module_path)
        assert _class.Historical == HistoricalDataTask


def test_get_class_object_module_not_found(task_creator):
    module_path = "invalid.module.path"

    with patch("importlib.import_module", side_effect=ModuleNotFoundError):
        with pytest.raises(
            TaskCreationError,
            match="Cannot create task, task specific module not found",
        ):
            task_creator._get_class_object(module_path)


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
