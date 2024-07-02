from enum import Enum, auto, StrEnum


class RunState(Enum):
    """Enum to represent the state of a task."""

    RUN = auto()  # Task needs to be run still
    DONE = auto()  # Task has been run


class TaskType(Enum):
    """Enum to represent the type of a task."""

    IO = auto()  # Task is IO bound
    CPU = auto()  # Task is cpu bound


class DataCategory(StrEnum):
    """Enum mapping Data Categoreis to the appropiate Task subclass."""

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
        """Returns the class path associated with a DataCategory member."""
        category_to_class_map = {
            DataCategory.HISTORICAL: "data_gathering.data.historical.historical_task.HistoricalDataTask"
        }
        return category_to_class_map.get(self, None)  # Return None if not found
