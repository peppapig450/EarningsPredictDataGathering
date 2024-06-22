from enum import Enum, auto, StrEnum
from typing import Dict


class RunState(Enum):
    """Enumeration to represent the state of a task."""

    RUN = auto()  # task needs to be run still
    DONE = auto()  # task has been run


class TaskType(Enum):
    """Enumeration to represent the type of a task."""

    IO = auto()  # task is io bound
    CPU = auto()  # task is cpu bound


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


class TaskMeta(type):
    """
    Metaclass for Task to dynmically create a Task subclass based on the data category
    and enforce that this created class has the required methods.
    """

    def __call__(cls, *args, **kwargs):
        data_category = kwargs.get("data_category")
        data_category_task_class = cls.get_data_category_class(data_category)

        # TODO: read this and look at below https://stackoverflow.com/questions/392160/what-are-some-concrete-use-cases-for-metaclasses
        # experiminting in 'test.py'
        # Figure how how to get the namespace for the class. call init ?
        # __prepare__ is probably good here too
        # Dynamically create a new subclass of cls with data_category_task_class as the base class
        CategoryClass = type(data_category_task_class, (cls,), {})

        # Make sure the required methods exist, this eliminates the need for an abstract class
        if not hasattr(CategoryClass, "run_io") or not hasattr(
            CategoryClass, "run_cpu"
        ):
            raise TypeError(
                f"Class '{CategoryClass}' must implement 'run_io' and 'run_cpu' methods"
            )

        # Create a new instance of the dynamically created class
        instance = super(TaskMeta, cls).__call__(*args, **kwargs)
        return instance

    @classmethod
    def get_data_category_class(mcs, data_category: DataCategory) -> str:
        """
        Returns the name of the data processor class corresponding to the given data category.

        Args:
            data_category (DataCategory): The data category.

        Returns:
            str: The name of the data processor class.
        """
        return data_category.value
