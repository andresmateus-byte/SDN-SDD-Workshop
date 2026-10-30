class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code, self.message, self.status_code = code, message, status_code

class TopologyLoadError(RuntimeError):
    """Fatal startup error for an absent or invalid topology file."""
