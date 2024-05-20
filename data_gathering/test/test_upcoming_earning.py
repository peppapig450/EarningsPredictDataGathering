from data_gathering.models.symbols import Symbol
from data_gathering.models.upcoming_earning import UpcomingEarning


def test_upcoming_earning_initialization():
    # Test the initialization of an UpcomingEarning object
    symbol = Symbol("AAPL")
    earning_date = "2024-05-30"
    earning = UpcomingEarning(symbol, earning_date)
    assert earning.symbol == symbol
    assert earning.earnings_date == earning_date


def test_upcoming_earning_represenation():
    symbol = Symbol("AAPL")
    earning_date = "2024-05-30"
    earning = UpcomingEarning(symbol, earning_date)
    assert (
        repr(earning)
        == f"UpcomingEarning(symbol={symbol}, earnings_date={earning_date})"
    )
