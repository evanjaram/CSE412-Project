class MissingParameterError(Exception):
    def __init__(self, message="Missing or invalid query parameter"):
        super().__init__(message)
        self.message = message

class EmptyQueryOutputError(Exception):
    def __init__(self, message="Query returned no rows"):
        super().__init__(message)
        self.message = message