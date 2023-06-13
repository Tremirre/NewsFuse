class FailedToLoadModelException(Exception):
    """Raised when a model fails to load"""

    def __init__(self, model_name):
        self.message = "Failed to load model: " + model_name
        super().__init__(self.message)
