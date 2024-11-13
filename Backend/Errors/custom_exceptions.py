class MissingParameterError(Exception):
    def __init__(self, message="Missing query parameter"):
        super().__init__(message)
        self.message = message
        self.status_code = 400

class UnknownParameterError(Exception):
    def __init__(self, message="Unknown query parameter"):
        super().__init__(message)
        self.message = message
        self.status_code = 400

class EmptyQueryOutputError(Exception):
    def __init__(self, message="Query returned no rows"):
        super().__init__(message)
        self.message = message
        self.status_code = 420


class IncorrectParameterFormError(Exception):
    def __init__(self, message="Incorrect query parameter form"):
        super().__init__(message)
        self.message = message
        self.status_code = 400