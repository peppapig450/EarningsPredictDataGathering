from math import floor
from typing import Any, Self

from itertools import islice, count

type Symbols = list[str]


# TODO: maybe rename
class BatchIteratorWithCount:
    """
    An iterator that processes an iterable in batches, keeping a count of the
    number of items consumed. The batch size is determined as a fraction of the
    total number of items in the iterable.

    Attributes:
        _it (iter): The underlying iterator of the provided iterable.
        _batch_size (int): The number of items in each batch.
        _count (itertools.count): A counter to keep track of the number of batches.
        _total_seen (int): The total number of items processed.

    Methods:
        __iter__(): Returns the iterator object.
        __next__(): Returns the next batch of items and the current batch count.
        total_seen(): Returns the total number of items processed (read-only property).
    """

    def __init__(self, iterable: Symbols, fraction: float = 0.1) -> None:
        """
        Initialize the BatchIteratorWithCount.

        Args:
            iterable (Symbols): The input iterable to be processed in batches.
            fraction (float): The fraction of the total items to determine the batch size.
        """
        self._it = iter(iterable)
        self._batch_size = self._calculate_batch_size(iterable, fraction)
        self._count = count(start=1)
        self._total_seen = 0

    def __iter__(self) -> Self:
        """
        Returns the iterator object.

        Returns:
            BatchIteratorWithCount: The iterator object itself.
        """
        return self

    def __next__(self) -> tuple[tuple[Any, ...], int]:
        """
        Returns the next batch of items and the current batch count.

        Returns:
            Tuple[Tuple[Any, ...], int]: A tuple containing the next batch of items and the batch count.

        Raises:
            StopIteration: When there are no more items to process.
        """
        batch = tuple(islice(self._it, self._batch_size))
        if not batch:
            raise StopIteration

        self._total_seen += len(batch)

        return batch, next(self._count)

    @property
    def total_seen(self) -> int:
        """
        Getter method to access the total number of elements seen (read-only).
        """
        return self._total_seen

    @property
    def batch_size(self) -> int:
        """
        Getter method to access the batch size that was calculated (read-only).
        """
        return self._batch_size

    def _calculate_batch_size(self, iterable: Symbols, fraction: float) -> int:
        return max(1, floor(len(iterable) * fraction))
