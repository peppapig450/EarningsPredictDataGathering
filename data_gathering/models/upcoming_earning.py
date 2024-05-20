from .symbols import Symbol


class UpcomingEarning:
    def __init__(self, symbol: Symbol, earnings_date: str):
        self.symbol = symbol
        self.earnings_date = earnings_date

    def __repr__(self) -> str:
        return (
            f"UpcomingEarning(symbol={self.symbol}, earnings_date={self.earnings_date})"
        )
