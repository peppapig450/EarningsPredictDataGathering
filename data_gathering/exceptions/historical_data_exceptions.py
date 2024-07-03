from .project_base_exception import EarningsPredictError


class HistoricalDataError(EarningsPredictError):
    """Exception pertaining to the Historical Data Gathering/Processing Functionality"""

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message, notes, include_traceback)


class HistoricalDataGatheringError(HistoricalDataError):
    """Exception for an exception occuring while gathering Historical Data"""

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message, notes, include_traceback)
