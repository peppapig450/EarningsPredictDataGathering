from more_itertools import windowed


class SymbolIterator:
    def __init__(self, symbols, batch_size=None, process_count=1):
        self.symbols = symbols
        self.process_count = process_count
        self.batch_size = (
            batch_size if batch_size is not None else self.calculate_batch_size()
        )

    def __len__(self):
        # calculate and return length of symbols
        if hasattr(self.symbols, "__len__"):
            return len(self.symbols)
        else:
            return 0

    def calculate_batch_size(self):
        if self.process_count <= 1:
            return len(self.symbols) // 4
        else:
            symbols_length = len(self.symbols)
            return (symbols_length + self.process_count - 1) // self.process_count

    def __iter__(self):
        for batch in windowed(
            self.symbols, self.batch_size, fillvalue=None, step=self.batch_size
        ):
            yield batch
