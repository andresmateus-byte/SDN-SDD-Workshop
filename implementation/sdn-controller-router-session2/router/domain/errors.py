class RouterAppError(Exception):
    def __init__(self, code: str, message: str, status_code: int, packet_id: str | None = None):
        super().__init__(message); self.code, self.message, self.status_code, self.packet_id = code, message, status_code, packet_id

class ControllerUnavailableError(Exception): pass
class ControllerApplicationError(Exception):
    def __init__(self, code, message): super().__init__(message); self.code, self.message = code, message
