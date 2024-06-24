from typing import Any, Optional
from abc import ABC, abstractmethod
from enum import Enum, auto, StrEnum
from data_gathering.utils.safe_uuid import generate_safe_uuid

type Window = tuple[tuple[Any, ...], int]


class RunState(Enum):
    """Enum to represent the state of a task."""

    RUN = auto()  # Task needs to be run still
    DONE = auto()  # Task has been run


class TaskType(Enum):
    """Enum to represent the type of a task."""

    IO = auto()  # Task is IO bound
    CPU = auto()  # Task is cpu bound


class DataCategory(StrEnum):
    """Enum mapping Data Categories to the appropiate Task subclass"""

    HISTORICAL = "HistoricalDataTask"  # Historical Price Data
    FUNDAMENTALS = "FundamentalMetricsTask"  # Fundamental Metrics
    ANALYST_ESTIMATES = "AnalysistEstimatesTask"  # Analyst Estimates and Recommendation
    MARKET_SENTIMENT = "MarketSentimentIndicatorsTask"  # Market Sentiment Indicators
    INDUSTRY_SECTOR = "IndustryAndSectorDataTask"  # Industry and Sector data
    COMPANY_NEWS = "CompanyNewsAndEventsTask"  # Company News and Events
    VOLATILITY = "VolatilityTradingVolumeTask"  # Volatility and trading volume
    EARNINGS_TRANSCRIPTS = "EarningsTranscriptsTask"  # Past earnings call transcripts

    @classmethod
    def get_task_class_path(cls, self):
        """Returns the class name associated with a DataCategory member."""
        # XXX: implement the others as they're written
        category_to_class_map = {
            DataCategory.HISTORICAL: "data_gathering.data.historical.historical_task.HistoricalDataTask"
        }
        return category_to_class_map.get(self, None)  # Return None if not found


class Task(ABC):
    """
    A class representing a task with specific attributes and state.

    Attributes:
    ----------
        task_id (str): The unique identifier of the task, generated using a safe UUID.
        task_type (TaskType): The type of task (IO or CPU bound).
        data_category (DataCategory): The category of data the task handles.
        state (RunState): The current state of the task (RUN or DONE).
        io_result (Optional[Any]): The result of the IO operation, initially None.
        cpu_result (Optional[Any]): The result of the CPU operation, initially None.
        data_category_class (Optional[str]): The data category class name, assigned by the metaclass.
        symbols (Symbols): A window of symbols related to the task.
        symbols_seen (int): The number of symbols seen.

    Note:
        The `task_id` is automatically generated using a safe UUID to ensure uniqueness across
        multiple processes. This ensures each task has a unique identifier without the risk of collisions.
    """

    __slots__ = (
        "task_id",
        "task_type",
        "data_category",
        "state",
        "io_result",
        "cpu_result",
        "symbols",
        "symbols_seen",
    )

    def __init__(
        self,
        *,
        task_type: TaskType,
        data_category: DataCategory,
        symbols: Window,
        symbols_seen: int,
    ) -> None:
        """
        Initializes a Task instance.

        Args:
            task_type (TaskType): The type of task (IO or CPU bound).
            data_category (DataCategory): The category of data the task handles.
            symbols (Window): A window of symbols related to the task.
            symbols_seen (int): The number of symbols seen.
        """
        self.task_id: str = generate_safe_uuid()
        self.task_type: TaskType = task_type
        self.data_category: DataCategory = data_category
        self.state: RunState = RunState.RUN
        self.io_result: Any | None = None
        self.cpu_result: Any | None = None
        self.symbols: Window = symbols
        self.symbols_seen: int = symbols_seen

    @abstractmethod
    def run_io(self):
        """Abstract method to ensure that all subclasses of Task have a function for IO bound tasks."""

    @abstractmethod
    def run_cpu(self):
        """Abstract method to ensure that all subclasses of Task have a function for CPU bound tasks."""
