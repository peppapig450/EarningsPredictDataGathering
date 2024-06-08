# Custom exceptions


class NoUpcomingEarningsError(Exception):
    def __init__(
        self,
        message="Error occured while retrieving upcoming earnings list. parsed_data empty.",
    ):
        super().__init__(message)
        raise RuntimeError from self
