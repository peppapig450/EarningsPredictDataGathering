from .project_base_exception import EarningsPredictError

class SymbolsFilteringError(EarningsPredictError):
    """
    Exception raised for an exception that occurs while symbols are being filtered.
    """

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message, notes, include_traceback)