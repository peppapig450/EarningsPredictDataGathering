from itertools import cycle
from math import floor
from typing import Iterator, List

from more_itertools import windowed

from .upcoming_earning import UpcomingEarning


class UpcomingEarningsIterator:
    def __init__(self, earnings: List[UpcomingEarning]):
        self.symbols = [earning.symbol for earning in earnings]
        self.index = 0  # For tracking the current index for __next__

    def __iter__(self) -> Iterator[str]:
        self.index = 0  # Reset the index whenever we start a new iteration
        return self

    def __next__(self) -> str:
        if self.index >= len(self.symbols):
            raise StopIteration
        symbol = self.symbols[self.index]
        self.index += 1
        return symbol

    def cyclic_iterator(self) -> Iterator[str]:
        return cycle(self.symbols)

    def window_iterator(
        self, fraction: float = 0.1
    ) -> Iterator[tuple[str | None, ...]]:
        total_symbols = len(self.symbols)
        window_size = max(1, floor(total_symbols * fraction))
        return windowed(self.symbols, window_size, step=window_size)
