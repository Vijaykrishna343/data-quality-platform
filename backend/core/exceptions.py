class DatasetNotFoundException(Exception):
    def __init__(self, message="Dataset not found"):
        self.message = message
        super().__init__(self.message)


class CleaningException(Exception):
    def __init__(self, message="Cleaning failed"):
        self.message = message
        super().__init__(self.message)