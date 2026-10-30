from typing import Protocol
from router.domain.models import ForwardingResult
class ForwardingLogDAO(Protocol):
    def save(self, result: ForwardingResult) -> None: ...
