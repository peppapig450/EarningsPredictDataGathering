from enum import Enum, auto
from typing import Any


class RunState(Enum):
    RUN = auto()  # task needs to be run still
    DONE = auto()  # task has been run


class TaskType(Enum):
    IO = auto()  # task is io bound
    CPU = auto()  # task is cpu bound


class DataCategory(Enum):
    HISTORICAL = auto()  # Historical Price Data
    FUNDAMENTALS = auto()  # Fundamental Metrics
    ANALYST_ESTIMATES = auto()  # Analyst Estimates and Recommendation
    MARKET_SENTIMENT = auto()  # Market Sentiment Indicators
    INDUSTRY_SECTOR = auto()  # Industry and Sector data
    COMPANY_NEWS = auto()  # Company News and Events
    VOLATILITY = auto()  # Volatility and trading volume
    EARNINGS_TRANSCRIPTS = auto()  # Past earnings call transcripts

    @property
    def get_next_category(self):
        current_index = list(DataCategory).index(self)
        next_index = (current_index + 1) % len(DataCategory)
        return DataCategory(next_index + 1)


class TaskMeta(type):
    def __call__(cls, *args, **kwargs):
        data_processor_class = cls.get_data_processor(kwargs["data_category"])
        # Make sure the required methods exist, this eliminates the need for an abstract class
        if not hasattr(cls, "run_io") or not hasattr(cls, "run_cpu"):
            raise TypeError(
                f"Class '{cls.__name__}' must implement 'run_io' and 'run_cpu' methods"
            )
        instance = super().__call__(*args, **kwargs)
        instance.data_procsessor_class = data_processor_class
        return instance

    @classmethod
    def get_data_processor(cls, data_category):
        mapping = {
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
