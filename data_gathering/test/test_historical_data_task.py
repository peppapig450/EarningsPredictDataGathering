import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from multiprocessing import Queue
import pytest

from data_gathering.config.api_keys import APIKeys
from data_gathering.data.historical.historical_task import HistoricalDataTask
from data_gathering.data.historical.historical_data_session import (
    HistoricalDataSessionManager,
)
from data_gathering.data.historical.historical_gathering import HistoricalDataGathering
from data_gathering.tasks.task_enums import TaskType, DataCategory


@pytest.fixture
def api_keys():
    return APIKeys(load_from="config")


@pytest.fixture
def session_manager(api_keys):
    return HistoricalDataSessionManager(api_keys)


@pytest.fixture
def dates():
    return {"from_date": "2022-01-01", "to_date": "2022-12-31"}


@pytest.fixture
def symbols():
    return ("AAPL", "GOOGL")


@patch("data_gathering.data.historical.historical_task.HistoricalDataGathering")
@patch("data_gathering.data.historical.historical_task.HistoricalDataSessionManager")
def test_run_io(
    MockSessionManager, MockGathering, api_keys, session_manager, dates, symbols
):
    mock_session_manager_instance = MockSessionManager.return_value
    mock_gathering_instance = MockGathering.return_value

    mock_gathering_instance.make_api_request = AsyncMock(
        return_value=({"data": "some_data", "next_page_token": None}, "complete_url")
    )
    mock_gathering_instance.handle_response_pagination = AsyncMock(
        return_value={"data": "complete_data"}
    )

    task = HistoricalDataTask(
        task_type=TaskType.IO,
        data_category=DataCategory.HISTORICAL,
        symbols=symbols,
        symbols_seen=0,
        api_keys=api_keys,
        session_manager=mock_session_manager_instance,
        dates=dates,
    )

    cpu_queue = Queue()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task.run_io(cpu_queue))

    gathered_data = cpu_queue.get()
    assert gathered_data == {"data": "complete_data"}

    mock_gathering_instance.make_api_request.assert_called_once_with(
        mock_session_manager_instance.manage_session().__enter__(), symbols
    )
    mock_gathering_instance.handle_response_pagination.assert_called_once_with(
        mock_session_manager_instance.manage_session().__enter__(),
        {"data": "some_data", "next_page_token": None},
        "complete_url",
    )

    loop.close()


@pytest.mark.asyncio
async def test_gather_data_for_symbols(api_keys, session_manager, dates, symbols):
    mock_gathering = MagicMock(spec=HistoricalDataGathering)
    mock_gathering.make_api_request = AsyncMock(
        return_value=({"data": "some_data", "next_page_token": None}, "complete_url")
    )
    mock_gathering.handle_response_pagination = AsyncMock(
        return_value={"data": "complete_data"}
    )

    task = HistoricalDataTask(
        task_type=TaskType.IO,
        data_category=DataCategory.HISTORICAL,
        symbols=symbols,
        symbols_seen=0,
        api_keys=api_keys,
        session_manager=session_manager,
        dates=dates,
    )
    task.worker = mock_gathering

    gathered_data = await task._gather_data_for_symbols(symbols)
    assert gathered_data == {"data": "complete_data"}
    mock_gathering.make_api_request.assert_called_once()
    mock_gathering.handle_response_pagination.assert_called_once()
