from enum import Enum, auto
from typing import Dict


class RunState(Enum):
    """Enumeration to represent the state of a task."""

    RUN = auto()  # task needs to be run still
    DONE = auto()  # task has been run


class TaskType(Enum):
    """Enumeration to represent the type of a task."""

    IO = auto()  # task is io bound
    CPU = auto()  # task is cpu bound


# XXX: look into using a dataclass mixin with the enum to avoid having to use the mapping
# XXX: or use a plain string enum https://docs.python.org/3/howto/enum.html#enum-dataclass-support
class DataCategory(Enum):
    """Enumeration to represent different categories of data."""

    HISTORICAL = auto()  # Historical Price Data
    FUNDAMENTALS = auto()  # Fundamental Metrics
    ANALYST_ESTIMATES = auto()  # Analyst Estimates and Recommendation
    MARKET_SENTIMENT = auto()  # Market Sentiment Indicators
    INDUSTRY_SECTOR = auto()  # Industry and Sector data
    COMPANY_NEWS = auto()  # Company News and Events
    VOLATILITY = auto()  # Volatility and trading volume
    EARNINGS_TRANSCRIPTS = auto()  # Past earnings call transcripts

    @property
    def get_next_category(self) -> "DataCategory":
        """
        Returns the next data category in a cyclic manner.

        Returns:
            DataCategory: The next data category.
        """
        current_index = list(DataCategory).index(self)
        next_index = (current_index + 1) % len(DataCategory)
        return DataCategory(next_index + 1)


class TaskMeta(type):
    """
    Metaclass for Task to enforce the implementation of required methods and
    assign the appropriate data processor class based on the data category.
    This way we do not need an abstract class.
    """

    def __call__(cls, *args, **kwargs):
        data_category_class = cls.get_data_category_class(kwargs["data_category"])
        # Make sure the required methods exist, this eliminates the need for an abstract class
        if not hasattr(cls, "run_io") or not hasattr(cls, "run_cpu"):
            raise TypeError(
                f"Class '{cls.__name__}' must implement 'run_io' and 'run_cpu' methods"
            )
        instance = super().__call__(*args, **kwargs)
        instance.data_category_class = data_category_class
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
        mapping: Dict[DataCategory, str] = {
            DataCategory.HISTORICAL: "HistoricalDataTask",
            DataCategory.FUNDAMENTALS: "FundamentalMetricsTask",
            DataCategory.ANALYST_ESTIMATES: "AnalysistEstimatesTask",
            DataCategory.MARKET_SENTIMENT: "MarketSentimentIndicatorsTask",
            DataCategory.INDUSTRY_SECTOR: "IndustryAndSectorDataTask",
            DataCategory.COMPANY_NEWS: "CompanyNewsAndEventsTask",
            DataCategory.VOLATILITY: "VolatilityTradingVolumeTask",
            DataCategory.EARNINGS_TRANSCRIPTS: "EarningsTranscriptsTask",
        }
        return mapping[data_category]
