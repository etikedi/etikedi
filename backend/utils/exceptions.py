class ValidationError(ValueError):
    def __init__(self, message: str):
        self.message: str = message
