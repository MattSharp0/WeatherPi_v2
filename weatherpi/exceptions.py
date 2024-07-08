class DataError(Exception):
    def __init__(self, m, *args):
        super().__init__(args)
        self.m = m

    def __str__(self):
        return f"DataError: {self.m}"
